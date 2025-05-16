# backend_api/main.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pyswip import Prolog
import os 
from pathlib import Path

app = FastAPI(
    title="Chatbot Backend API",
    description="API for interacting with the Prolog knowledge base.",
    version="0.1.0"
)

# --- CORS Configuration ---
origins = [
    "http://localhost",
    "http://localhost:8080", 
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "null", 
    # Add your frontend development server origin if different
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- END CORS Configuration ---


# --- Pydantic Models for Request/Response ---
class ChatQuery(BaseModel):
    user_message: str
    session_id: str = "default_session"

class ChatResponse(BaseModel):
    bot_response: str
    query_used: str

# --- Prolog Initialization ---
prolog = Prolog()
kb_path_for_prolog = ""
try:
    current_script_dir = Path(__file__).resolve().parent
    kb_path_obj = current_script_dir / "knowledge_base.pl"
    kb_path_for_prolog = kb_path_obj.as_posix()
    if not kb_path_obj.is_file():
        print(f"CRITICAL ERROR: Knowledge base file not found at {kb_path_obj}")
    else:
        print(f"Attempting to consult Prolog knowledge base: {kb_path_for_prolog}")
        consult_query_string = f"consult('{kb_path_for_prolog}')"
        print(f"Executing manual Prolog consult query: {consult_query_string}")
        list(prolog.query(consult_query_string)) 
        print(f"Successfully consulted: {kb_path_for_prolog} using manual query.")
except Exception as e:
    path_debug = kb_path_for_prolog if kb_path_for_prolog else "Path construction might have failed"
    prolog_cause_message = ""
    if hasattr(e, 'args') and e.args:
        prolog_cause_message = str(e.args[0]) if len(e.args) > 0 else ""
    print(f"CRITICAL ERROR: Could not consult Prolog file. Path used: '{path_debug}'. Caused by: '{prolog_cause_message}': {e}")
    print("Ensure SWI-Prolog is installed and in your system PATH.")
    print("Also, check that the knowledge_base.pl file exists and is correctly formatted.")

# --- Helper function to query Prolog and format results ---
def query_prolog_kb(prolog_query_str: str):
    try:
        print(f"Executing Prolog query: {prolog_query_str}")
        solutions = list(prolog.query(prolog_query_str))
        print(f"Solutions found: {solutions}")
        if not solutions: return None
        if solutions == [{}]: return "Fact processed or query is true."
        
        results = []
        for sol_dict in solutions:
            if not sol_dict: continue
            if len(sol_dict) == 1: 
                val = list(sol_dict.values())[0]
                if isinstance(val, list): 
                    results.append(", ".join(str(v_item) for v_item in val))
                else: 
                    results.append(str(val))
            else: 
                results.append("; ".join(f"{str(k)}: {str(v)}" for k, v in sol_dict.items()))
        return results[0] if len(results) == 1 else results if results else None
    except Exception as e:
        print(f"Prolog query failed: {prolog_query_str} - Error: {e}")
        raise HTTPException(status_code=500, detail=f"Prolog query error for '{prolog_query_str}': {e}")

@app.post("/chat", response_model=ChatResponse)
async def chat_with_bot(query: ChatQuery):
    user_message = query.user_message.lower().strip() # Original user message is lowercased and stripped
    # For emoji check, we need the original stripped message before lowercasing if emojis have case sensitivity
    # However, standard emojis are unicode characters and .lower() typically doesn't affect them.
    # So, using the already processed user_message for emoji check is fine.
    
    prolog_q_made = ""
    
    greeting_response_text = "Hello! I am a chatbot representing Mr. Dhinesh E. Feel free to ask any professional questions about him."
    greetings = ["hello", "hi", "hai", "hey", "good morning", "good afternoon", "good evening"]
    
    # --- START: Definition of heart emojis and their specific response ---
    heart_emojis = {
        "❤️", "🧡", "💛", "💚", "💙", "💜", "🤎", "🖤", "🤍", 
        "💖", "💗", "💓", "💞", "💕", "💘", "💝", "💟", "💔", "❣️", "🤞"
    }
    heart_emoji_response_text = "Thanks for your love. ❤️🤞"
    # --- END: Definition of heart emojis ---

    response_text = "I'm not sure how to respond to that. Please try rephrasing your question about Mr. Dhinesh E."

    if user_message in greetings:
        response_text = greeting_response_text
        prolog_q_made = "greeting_intent"
    elif user_message in heart_emojis: # Check if the *entire* stripped message is one of the heart emojis
        response_text = heart_emoji_response_text
        prolog_q_made = "heart_emoji_love_intent"
    else:
        # If not a greeting and not a standalone heart emoji, proceed with other intent matching
        try:
            # Profile Information
            if "your name" in user_message or user_message == "name" or "what is your name" in user_message:
                prolog_q_made = "name(X)"
                result = query_prolog_kb(prolog_q_made)
                # The user updated this response in the provided code, so I'm keeping it.
                if result and result != "Fact processed or query is true.": response_text = f"My name is BytePersona which is developed by Tharik MCA and here to represent {result}."
                else: response_text = "I don't have a specific name assigned in my knowledge base."
            elif "email" in user_message:
                prolog_q_made = "email(X)"
                result = query_prolog_kb(prolog_q_made)
                if result and result != "Fact processed or query is true.": response_text = f"The email is {result}."
                else: response_text = "I don't have an email address listed for Mr. Dhinesh E."
            elif "phone" in user_message or "contact number" in user_message:
                prolog_q_made = "phone(X)"
                result = query_prolog_kb(prolog_q_made)
                if result and result != "Fact processed or query is true.": response_text = f"The contact number is {result}."
                else: response_text = "I don't have a phone number listed for Mr. Dhinesh E."
            elif "location" in user_message or "where are you" in user_message or "where do you live" in user_message :
                prolog_q_made = "location(X)"
                result = query_prolog_kb(prolog_q_made)
                if result and result != "Fact processed or query is true.": response_text = f"Mr. Dhinesh E. is based in {result}."
                else: response_text = "I don't have location information for Mr. Dhinesh E."
            elif user_message == "age" or "your age" in user_message or "how old are you" in user_message or "what is your age" in user_message:
                prolog_q_made = "age(X)"
                result = query_prolog_kb(prolog_q_made)
                if result and result != "Fact processed or query is true.": response_text = f"Mr. Dhinesh E. is {result} years old."
                else: response_text = "I don't have age information for Mr. Dhinesh E."
            elif "father's name" in user_message or "father name" in user_message:
                prolog_q_made = "father_name(X)"
                result = query_prolog_kb(prolog_q_made)
                if result and result != "Fact processed or query is true.": response_text = f"Mr. Dhinesh E.'s father's name is {result}."
                else: response_text = "I don't have information about Mr. Dhinesh E.'s father's name."
            elif "mother's name" in user_message or "mother name" in user_message:
                prolog_q_made = "mother_name(X)"
                result = query_prolog_kb(prolog_q_made)
                if result and result != "Fact processed or query is true.": response_text = f"Mr. Dhinesh E.'s mother's name is {result}."
                else: response_text = "I don't have information about Mr. Dhinesh E.'s mother's name."
            elif "parent" in user_message or "parents" in user_message:
                father_name_result = query_prolog_kb("father_name(X)")
                mother_name_result = query_prolog_kb("mother_name(X)")
                parent_responses = []
                queries_made_list = []
                if father_name_result and father_name_result != "Fact processed or query is true.":
                    parent_responses.append(f"Father's name is {father_name_result}.")
                    queries_made_list.append("father_name(X)")
                if mother_name_result and mother_name_result != "Fact processed or query is true.":
                    parent_responses.append(f"Mother's name is {mother_name_result}.")
                    queries_made_list.append("mother_name(X)")
                if parent_responses: response_text = "Regarding Mr. Dhinesh E.'s parents: " + " ".join(parent_responses)
                else: response_text = "I don't have information about Mr. Dhinesh E.'s parents to share."
                prolog_q_made = ", ".join(queries_made_list) if queries_made_list else "Checked for parent names"
            
            # Hobbies
            elif "hobbies" in user_message or "hobby" in user_message:
                prolog_q_made = "hobby(Hobby)"
                results = query_prolog_kb(prolog_q_made) 
                hobbies_list = []
                if isinstance(results, list):
                    hobbies_list = [str(item) for item in results if item and item != "Fact processed or query is true."]
                elif results and results != "Fact processed or query is true.":
                    hobbies_list.append(str(results))
                if hobbies_list: response_text = f"Mr. Dhinesh E.'s hobbies include: {', '.join(hobbies_list)}."
                else: response_text = "I don't have information about Mr. Dhinesh E.'s hobbies right now."

            # Technical Skills
            elif "programming languages" in user_message or "coding languages" in user_message or \
                 "technical skills" in user_message or "skills" in user_message or user_message == "skill":
                prolog_q_made = "language(L), web_technology(W), database(D)" 
                def get_skills_from_kb(query, category_name):
                    items = query_prolog_kb(query)
                    if items and items != "Fact processed or query is true.":
                        items_list = items if isinstance(items, list) else [items]
                        valid_items = [str(item) for item in items_list if item and item != "Fact processed or query is true."]
                        if valid_items:
                            return f"{category_name}: {', '.join(valid_items)}"
                    return None
                skills_parts = [
                    get_skills_from_kb("language(L)", "Programming Languages"),
                    get_skills_from_kb("web_technology(W)", "Web Technologies"),
                    get_skills_from_kb("database(D)", "Databases")
                ]
                valid_skills_parts = [s for s in skills_parts if s]
                if valid_skills_parts:
                    response_text = "Mr. Dhinesh E.'s technical skills include:\n- " + "\n- ".join(valid_skills_parts)
                else:
                    response_text = "I haven't listed Mr. Dhinesh E.'s technical skills."

            # Spoken Languages
            elif "languages do you speak" in user_message or "spoken languages" in user_message or \
                 "spoken language" in user_message or user_message == "languages" or "what languages" in user_message:
                prolog_q_made = "language_known(Lang)"
                results = query_prolog_kb(prolog_q_made)
                processed_results = []
                if results:
                    results_list = results if isinstance(results, list) else [results]
                    for r_item in results_list:
                        if r_item and r_item != "Fact processed or query is true.": 
                            processed_results.append(str(r_item).replace('_', ' '))
                if processed_results: response_text = f"Mr. Dhinesh E. speaks: {', '.join(processed_results)}."
                else: response_text = "I haven't listed the languages Mr. Dhinesh E. speaks."

            # Education CGPA
            elif (("cgpa" in user_message or "grade" in user_message) and ("mca" in user_message or "master" in user_message or "bca" in user_message or "bachelor" in user_message)) or \
                 (("mca" in user_message or "master" in user_message or "bca" in user_message or "bachelor" in user_message) and ("cgpa" in user_message or "grade" in user_message)):
                degree_atom_in_kb = None
                degree_display_name = None
                if "mca" in user_message or "master" in user_message:
                    degree_atom_in_kb, degree_display_name = 'MCA', 'MCA'
                elif "bca" in user_message or "bachelor" in user_message:
                    degree_atom_in_kb, degree_display_name = 'BCA', 'BCA'
                if degree_atom_in_kb:
                    prolog_q_made = f"education('{degree_atom_in_kb}', _, _, _, CGPA)"
                    result = query_prolog_kb(prolog_q_made) 
                    if result and result != "Fact processed or query is true.":
                        response_text = f"Mr. Dhinesh E.'s CGPA in {degree_display_name} is {result}."
                    else:
                        response_text = f"I couldn't find the CGPA for {degree_display_name} for Mr. Dhinesh E."
                else: 
                    response_text = "Which degree's CGPA are you asking about (e.g., MCA or BCA) for Mr. Dhinesh E.?"
            
            # General Education
            elif "education" in user_message or "studied" in user_message or "academic" in user_message or "graduation" in user_message: 
                prolog_q_made = "education(Degree, Institute, Location, Year, CGPA)"
                results = query_prolog_kb(prolog_q_made) 
                edu_list_texts = []
                if isinstance(results, list):
                    for res_str in results:
                        if res_str == "Fact processed or query is true.": continue
                        parts = {k.strip(): v.strip() for k, v in (item.split(':', 1) for item in res_str.split(';'))}
                        edu_list_texts.append(f"{parts.get('Degree','N/A')} from {parts.get('Institute','N/A')}, {parts.get('Location','N/A')} (Year: {parts.get('Year','N/A')}, CGPA: {parts.get('CGPA','N/A')})")
                elif results and results != "Fact processed or query is true.": 
                    parts = {k.strip(): v.strip() for k, v in (item.split(':', 1) for item in results.split(';'))}
                    edu_list_texts.append(f"{parts.get('Degree','N/A')} from {parts.get('Institute','N/A')}, {parts.get('Location','N/A')} (Year: {parts.get('Year','N/A')}, CGPA: {parts.get('CGPA','N/A')})")
                if edu_list_texts: response_text = "Mr. Dhinesh E.'s educational background:\n- " + "\n- ".join(edu_list_texts)
                else: response_text = "I don't have detailed education information for Mr. Dhinesh E. to share."
            
            # Projects
            elif "projects" in user_message or "project details" in user_message:
                prolog_q_made = "project(Name, Description, Technologies)"
                results = query_prolog_kb(prolog_q_made) 
                project_list_texts = []
                if isinstance(results, list):
                    for res_str in results:
                        if res_str == "Fact processed or query is true.": continue
                        parts = {k.strip(): v.strip() for k, v in (item.split(':', 1) for item in res_str.split(';'))}
                        tech_str = parts.get('Technologies', 'Not specified')
                        project_list_texts.append(f"{parts.get('Name','Unknown Project')}: {parts.get('Description','No description')} (Technologies: {tech_str})")
                elif results and results != "Fact processed or query is true.": 
                    parts = {k.strip(): v.strip() for k, v in (item.split(':', 1) for item in results.split(';'))}
                    tech_str = parts.get('Technologies', 'Not specified')
                    project_list_texts.append(f"{parts.get('Name','Unknown Project')}: {parts.get('Description','No description')} (Technologies: {tech_str})")
                if project_list_texts: response_text = "Here are some of Mr. Dhinesh E.'s projects:\n- " + "\n- ".join(project_list_texts)
                else: response_text = "I haven't listed any projects for Mr. Dhinesh E."
            
            # Specific Project: NutriFlow
            elif "nutriflow project" in user_message:
                prolog_q_made = "project('NutriFlow', Description, Technologies)" 
                result = query_prolog_kb(prolog_q_made)
                if result and result != "Fact processed or query is true.":
                    parts = {k.strip(): v.strip() for k, v in (item.split(':', 1) for item in result.split(';'))}
                    response_text = f"The NutriFlow project for Mr. Dhinesh E. is described as: {parts.get('Description','N/A')}. Technologies used: {parts.get('Technologies', 'Not specified')}."
                else:
                    response_text = "I couldn't find details for the NutriFlow project for Mr. Dhinesh E."
            
            # Certifications
            elif "certifications" in user_message or "certificates" in user_message:
                prolog_q_made = "certification(Name, Issuer)"
                results = query_prolog_kb(prolog_q_made)
                cert_list_texts = []
                if isinstance(results, list):
                    for r_str in results:
                        if r_str == "Fact processed or query is true.": continue
                        parts = {k.strip(): v.strip() for k,v in (item.split(': ',1) for item in r_str.split('; '))}
                        cert_list_texts.append(f"{parts.get('Name')} by {parts.get('Issuer')}")
                elif results and results != "Fact processed or query is true.":
                    parts = {k.strip(): v.strip() for k, v in (item.split(': ', 1) for item in results.split('; '))}
                    cert_list_texts.append(f"{parts.get('Name')} by {parts.get('Issuer')}")
                if cert_list_texts: response_text = "Mr. Dhinesh E. has the following certifications:\n- " + "\n- ".join(cert_list_texts)
                else: response_text = "I haven't listed any certifications for Mr. Dhinesh E."
            
            # Interests
            elif "interest" in user_message or "area of interest" in user_message:
                prolog_q_made = "interest(I)"
                results = query_prolog_kb(prolog_q_made)
                interest_list = []
                if isinstance(results, list):
                    interest_list = [str(item) for item in results if item and item != "Fact processed or query is true."]
                elif results and results != "Fact processed or query is true.":
                    interest_list.append(str(results))
                if interest_list: response_text = f"Mr. Dhinesh E.'s areas of interest include: {', '.join(interest_list)}."
                else: response_text = "I haven't listed Mr. Dhinesh E.'s areas of interest."

            # Portfolio Link
            elif "portfolio" in user_message or \
                 "personal website" in user_message or \
                 "your website" in user_message or \
                 "portfolio link" in user_message or \
                 "your site" in user_message:
                prolog_q_made = "portfolio_link_intent"
                response_text = "This is Dhinesh E's personal portfolio website: https://dhinesh7-cit.github.io" # Ensured https
            
            # User's "lover" intent from provided code
            elif "lover" in user_message:
                prolog_q_made = "lover_intent" # Assuming this doesn't come from Prolog, or you'd query it
                response_text = "Mr. Dhinesh E.'s Lover is Sree Abirami."

            # Social/Profile Links (GitHub, LinkedIn, LeetCode)
            elif "github" in user_message: 
                prolog_q_made = "github(Link)"
                result = query_prolog_kb(prolog_q_made)
                if result and result != "Fact processed or query is true.": response_text = f"Mr. Dhinesh E.'s GitHub profile is: {result}"
                else: response_text = "I don't have a GitHub link for Mr. Dhinesh E. in my knowledge base."
            elif "linkedin" in user_message:
                prolog_q_made = "linkedin(Link)"
                result = query_prolog_kb(prolog_q_made)
                if result and result != "Fact processed or query is true.": response_text = f"Mr. Dhinesh E.'s LinkedIn profile is: {result}"
                else: response_text = "I don't have a LinkedIn link for Mr. Dhinesh E. in my knowledge base."
            elif "leetcode" in user_message:
                prolog_q_made = "leetcode(Link)"
                result = query_prolog_kb(prolog_q_made)
                if result and result != "Fact processed or query is true.": response_text = f"Mr. Dhinesh E.'s LeetCode profile is: {result}"
                else: response_text = "I don't have a LeetCode link for Mr. Dhinesh E. in my knowledge base."
            elif "profile link" in user_message or user_message == "links" or \
                 "all links" in user_message or "social link" in user_message or \
                 "socials" in user_message or "connect with me" in user_message or \
                 "find you online" in user_message :
                links_map = {
                    "GitHub": query_prolog_kb("github(X)"),
                    "LinkedIn": query_prolog_kb("linkedin(X)"),
                    "LeetCode": query_prolog_kb("leetcode(X)")
                }
                prolog_q_made = "github(X), linkedin(X), leetcode(X)"
                link_responses = []
                for platform, link_result in links_map.items():
                    if link_result and link_result != "Fact processed or query is true.":
                        link_responses.append(f"{platform}: {link_result}")
                if link_responses:
                    response_text = "You can find Mr. Dhinesh E. online here:\n- " + "\n- ".join(link_responses)
                else:
                    response_text = "I don't have any profile links listed for Mr. Dhinesh E. at the moment."
            
        except HTTPException: 
            raise
        except Exception as e: 
            print(f"Error during NLU or response formatting for message '{user_message}': {e}")
            prolog_q_made = prolog_q_made if prolog_q_made else "Error during intent processing"
            return ChatResponse(bot_response="Sorry, I encountered an internal error while processing your request.", 
                                query_used=prolog_q_made)

    return ChatResponse(bot_response=response_text, 
                        query_used=prolog_q_made if prolog_q_made else "No specific Prolog query/intent matched.")

if __name__ == "__main__":
    import uvicorn
    print("Starting Uvicorn server for backend_api.main:app on http://127.0.0.1:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)