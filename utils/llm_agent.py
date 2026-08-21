import os
import json
import re
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

def extract_text(content):
    """
    Safely extracts string content from LangChain's response.content,
    which can be a string or a list of blocks/parts (e.g. for Gemini models).
    """
    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, dict):
                text_parts.append(block.get("text", block.get("thinking", "")))
            elif isinstance(block, str):
                text_parts.append(block)
            elif hasattr(block, "get"):
                text_parts.append(block.get("text", ""))
            elif hasattr(block, "text"):
                text_parts.append(block.text)
            else:
                text_parts.append(str(block))
        return "".join(text_parts)
    return str(content)

def get_llm(provider, api_key, model_name=None):
    """
    Instantiates the selected LLM provider with the given API key.
    """
    if provider == "Google Gemini":
        if not api_key:
            raise ValueError("Gemini API Key is required.")
        selected_model = model_name if model_name else "gemini-3.6-flash"
        return ChatGoogleGenerativeAI(
            model=selected_model, 
            google_api_key=api_key, 
            temperature=0.2
        )
    elif provider == "OpenAI":
        if not api_key:
            raise ValueError("OpenAI API Key is required.")
        selected_model = model_name if model_name else "gpt-4o-mini"
        return ChatOpenAI(
            model=selected_model, 
            openai_api_key=api_key, 
            temperature=0.2
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")

def load_rti_guide():
    """
    Loads the RTI guide markdown content to be used as context for the chatbot.
    """
    try:
        # Resolve path relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        guide_path = os.path.join(current_dir, "..", "data", "rti_guide.md")
        if os.path.exists(guide_path):
            with open(guide_path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        print(f"Error loading RTI guide: {e}")
    return "RTI Act 2005 guide context is unavailable."

def chat_with_navigator(provider, api_key, chat_history, user_message, model_name=None):
    """
    Converses with the user about the RTI Act rules, procedures, and exemptions.
    - chat_history: List of tuples/dicts representing history (role, content)
    - user_message: The new query from the user
    """
    try:
        llm = get_llm(provider, api_key, model_name)
    except Exception as e:
        return f"Error initializing LLM: {str(e)}. Please check your API key and provider configuration in the sidebar."

    guide_context = load_rti_guide()

    system_prompt = f"""You are an expert Right to Information (RTI) Navigator and Legal Advisor specialized in the Right to Information Act, 2005 (India).
Your goal is to help citizens understand their rights, guide them on how to file RTIs, explain timelines, fees, and appeals, and answer questions accurately.

Use the following official guidelines and rules as your core knowledge base to answer questions:
---
{guide_context}
---

Rules of engagement:
1. Provide accurate, helpful, and concise answers based on the RTI Act 2005 rules.
2. If the user asks about something outside of RTI or legal rights in India, politely redirect them.
3. Be supportive and explain legal terms in simple, plain language.
4. If a question is about whether certain information is exempted, refer to Section 8(1) details provided in the context.
5. Provide step-by-step guidance for appeals if the user mentions their application was rejected or ignored.
"""

    # Prepare chat history messages for LangChain
    messages = [SystemMessage(content=system_prompt)]
    
    for msg in chat_history:
        if msg.get("role") == "user":
            messages.append(HumanMessage(content=msg.get("content")))
        elif msg.get("role") == "assistant":
            messages.append(AIMessage(content=msg.get("content")))
            
    messages.append(HumanMessage(content=user_message))
    
    try:
        response = llm.invoke(messages)
        return extract_text(response.content)
    except Exception as e:
        return f"An error occurred while calling the LLM API: {str(e)}"

def optimize_rti_queries(provider, api_key, category_name, department_name, raw_problem, selected_template_points, model_name=None):
    """
    Refines the user's raw problem and selected template points into a set of precise, 
    objective, and legally sound point-wise questions for the RTI application.
    """
    try:
        llm = get_llm(provider, api_key, model_name)
    except Exception as e:
        return {"error": f"LLM Initialization failed: {str(e)}"}

    template_points_str = "\n".join([f"- {pt}" for pt in selected_template_points]) if selected_template_points else "None selected."

    prompt = f"""You are an expert legal drafter specializing in filing Right to Information (RTI) requests under the RTI Act, 2005 (India).
Your task is to refine a citizen's raw problem description and optional template questions into a list of 4 to 6 highly effective, objective, and precise questions for an RTI application.

RTI Drafting Gold Rule:
- Public Information Officers (PIOs) can reject or ignore questions that ask for "why", "opinions", "justifications", or are subjective (e.g., "Why is the road broken?" or "Who is responsible for this delay?").
- Instead, questions MUST ask for specific "information", "documents", "records", "file notes", "inspections", "logs", "work orders", or "guidelines" (e.g., "Provide copies of work orders...", "Provide the daily progress report...", "Provide names and designations of officials...").

Inputs:
- **RTI Category**: {category_name}
- **Target Department**: {department_name}
- **Applicant's Raw Problem**: {raw_problem}
- **Pre-Selected Standard Questions**:
{template_points_str}

Instruction:
1. Review the raw problem and selected questions.
2. Formulate 4 to 6 precise, point-wise queries in English.
3. Ensure each query is objective, targets records/documents, and cannot be easily rejected by the PIO under Section 8.
4. Output your response ONLY as a JSON list of strings. Do not include any markdown formatting or extra text outside the JSON block.

Expected Output Format:
[
  "Query 1 here",
  "Query 2 here",
  "Query 3 here",
  "Query 4 here"
]
"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        response_text = extract_text(response.content)
        content = response_text.strip()
        
        # Clean up JSON if LLM returned markdown code blocks
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0].strip()
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0].strip()
            
        queries = json.loads(content)
        if isinstance(queries, list):
            return {"queries": queries}
        else:
            return {"error": "LLM did not return a valid list of queries.", "raw_response": response_text}
    except json.JSONDecodeError:
        # Fallback parsing in case JSON is malformed
        # Split by lines starting with numbers or bullet points
        lines = response_text.split("\n")
        queries = []
        for line in lines:
            line_cleaned = re.sub(r'^(\d+[\.\)]|\-\s*|\*\s*)', '', line.strip()).strip(' "\',')
            if line_cleaned and len(line_cleaned) > 10:
                queries.append(line_cleaned)
        if queries:
            return {"queries": queries}
        return {"error": "Failed to parse LLM response as JSON list.", "raw_response": response_text}
    except Exception as e:
        return {"error": f"Error during query optimization: {str(e)}"}
