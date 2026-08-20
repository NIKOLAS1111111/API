import os
from google import genai
from google.genai import types

GEMINI_API_KEY = os.getenv("gemini_api_key")
client = genai.Client(api_key=GEMINI_API_KEY)

Model_Name = "gemini-3.1-flash-lite"
Instruction =(
    "your an assistante e-commerce for shoptech clients"
    "respond according to the language the question is asked"
    "Greats the users by using their names and present you to be NIK-AI "
    "Use only the information below and images to answer to clients"
    "if you don't have an information tel you don't have and sujeste a similar one"
    "Give all the price and be polite and take in to consideration the languages"
    "be brief(4-5 pharses max), specific and efficient"
    "reply in english if question is in english and in french if question is in french"
)

def ask_gemini(user_question: str, context_data: list[dict]) -> str:
    context_text = format_context(context_data)

    prompt = f"""product info available :
{context_text}

cliente question : {user_question}
"""

    response = client.models.generate_content(
        model=Model_Name,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=Instruction,
        ),
    )
    return response.text

def format_context(rows: list[dict]) -> str:
    if not rows:
        return "Product not found."

    lines = []
    for r in rows:
        stock_status = "in store" if r.get("stock_qty", 0) > 0 else "stock expired"
        lines.append(
            f"- {r.get('name')} (catégorie: {r.get('category')}) | Prix: {r.get('list_price')} | "
            f"{stock_status} ({r.get('stock_qty')} unités)"
)
    return "\n".join(lines)