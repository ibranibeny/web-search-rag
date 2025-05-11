import asyncio
from duckduckgo_search import DDGS
from bs4 import BeautifulSoup
from langchain.docstore.document import Document
from playwright.async_api import async_playwright
from langchain.agents import AgentExecutor, initialize_agent, Tool
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

import os
import nest_asyncio
nest_asyncio.apply()
os.environ["OPENAI_API_KEY"] = "YOUR_KEY"  # 

# --- TOOL 1: Web Search ---
def search_sources(query, max_results):
    urls = []
    with DDGS() as ddgs:
        for result in ddgs.text(query, max_results=max_results * 2):
            url = result.get("href") or result.get("url")
            if url:
                urls.append(url)
            if len(urls) >= max_results:
                break
    return urls

# --- TOOL 2: Scrape Content ---
async def fetch_all_sources(urls):
    documents = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
        )

        for url in urls:
            try:
                page = await context.new_page()
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")

                text = None
                if "arxiv.org" in url:
                    tag = soup.find("blockquote", class_="abstract")
                    if tag:
                        text = tag.get_text(separator=" ", strip=True).replace("Abstract: ", "")
                elif "wikipedia.org" in url:
                    tag = soup.find("div", id="mw-content-text")
                    if tag:
                        text = tag.get_text(separator=" ", strip=True)
                elif "medium.com" in url:
                    tag = soup.find("article")
                    if tag:
                        text = tag.get_text(separator=" ", strip=True)
                else:
                    for t in soup(["script", "style", "noscript", "header", "footer", "nav"]):
                        t.decompose()
                    body = soup.find("body")
                    if body:
                        text = body.get_text(separator=" ", strip=True)

                if text and len(text) > 100:
                    documents.append(Document(page_content=text[:50000], metadata={"source": url}))
            except Exception as e:
                print(f"❌ {url} - {e}")
            finally:
                await page.close()

        await browser.close()
    return documents

# --- TOOL WRAPPERS ---
def sync_fetch_and_embed(query: str):
    urls = search_sources(query, max_results=10)
    docs = asyncio.run(fetch_all_sources(urls))
    embedding = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(docs, embedding)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    llm_rag = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm_rag,
        retriever=retriever,
        return_source_documents=True
    )
    response = qa_chain.invoke({"query": query})
    #print("\n📚 Sumber dari RAG:")
    #for i, doc in enumerate(response["source_documents"], 1):
    #    print(f"{i}. {doc.metadata['source']}")
    return response["result"]

# --- AGENT SETUP ---
rag_tool = Tool(
    name="WebRAG",
    func=sync_fetch_and_embed,
    description="Use this to answer needed Question from Internet."
)

llm_agent = ChatOpenAI(model="gpt-4", temperature=0.7)
agent = initialize_agent([rag_tool], llm_agent, agent_type="zero-shot-react-description", verbose=True)

llm_direct = ChatOpenAI(model="gpt-4", temperature=0.7)  # Non-RAG LLM

# --- RUN LOOP ---
print("\n🤖 Agentic AI Ready!, Comparing between RAG and Non-RAG")
print("Question (or 'exit'):\n")

while True:
    user_input = input("👤 You: ")
    if user_input.lower() in ["exit", "quit", "keluar"]:
        print("👋 Good Bye!")
        break

    try:
        # Non-RAG
        print("\n🧠 Answer w/o RAG:")
        print("-" * 80)
        direct_response = llm_direct.invoke(user_input)
        print(direct_response.content.strip())
        print("-" * 80)

        # RAG via Agent
        print("\n🧠 Answer with RAG:")
        print("-" * 80)
        rag_response = agent.run(user_input)
        print(rag_response)
        print("-" * 80)

    except Exception as e:
        print("❌ Terjadi kesalahan:", e)
