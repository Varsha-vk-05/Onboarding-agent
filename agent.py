"""
AI Agent module for answering questions and generating personalized onboarding plans.
"""

import os
from typing import List, Dict, Optional
try:
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables from .env file
except Exception:
    pass  # dotenv is optional

# Robust imports for different langchain/openai layouts. If langchain isn't
# available we provide a minimal fallback that uses the `openai` package so
# the agent can still run in environments without langchain installed.
ChatOpenAI = None
HumanMessage = None
SystemMessage = None
_import_errs = []
try:
    # Preferred modern langchain path
    from langchain_openai import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage
except Exception as e1:
    _import_errs.append(("langchain.chat_models", str(e1)))
    try:
        # Alternative packaging used by some installs
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage
    except Exception as e2:
        _import_errs.append(("langchain_openai", str(e2)))
        # Last-resort fallback: use openai directly
        try:
            import openai

            class _ChatOpenAIFallback:
                def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo", temperature: float = 0.7, **kwargs):
                    self.api_key = api_key or os.getenv("OPENAI_API_KEY")
                    openai.api_key = self.api_key
                    self.model = model
                    self.temperature = temperature

                def invoke(self, messages):
                    # messages: list of SystemMessage/HumanMessage or simple objects with .content
                    msg_list = []
                    for m in messages:
                        role = getattr(m, "role", None) or ("system" if m.__class__.__name__.lower().startswith("system") else "user")
                        content = getattr(m, "content", str(m))
                        msg_list.append({"role": role, "content": content})
                    resp = openai.ChatCompletion.create(model=self.model, messages=msg_list, temperature=self.temperature)
                    class _R: pass
                    r = _R()
                    # compatibility with langchain ChatOpenAI response expectations
                    r.content = resp.choices[0].message["content"] if resp and resp.choices else str(resp)
                    return r

                def __call__(self, messages):
                    return self.invoke(messages)

            ChatOpenAI = _ChatOpenAIFallback

            class HumanMessage:
                def __init__(self, content: str):
                    self.content = content
                    self.role = "user"

            class SystemMessage:
                def __init__(self, content: str):
                    self.content = content
                    self.role = "system"

        except Exception as e3:
            _import_errs.append(("openai_fallback", str(e3)))
            raise ImportError(
                "Could not import a supported LLM client for OnboardingAgent. Tried: " +
                ", ".join(f"{k}: {v}" for k, v in _import_errs) +
                ". Ensure 'langchain' or 'langchain_openai' or 'openai' is installed and listed in requirements.txt"
            ) from e3
from ingest import DocumentIngester
from db import Database


class OnboardingAgent:
    """AI agent for handling onboarding queries and plan generation."""
    
    def __init__(self, openai_api_key: str = None, model_name: str = "gpt-3.5-turbo"):
        """Initialize the AI agent."""
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable.")
        
        try:
            # Newer langchain API
            self.llm = ChatOpenAI(
                api_key=self.api_key,
                model=model_name,
                temperature=0.7
            )
        except TypeError:
            # Fallback for older versions
            self.llm = ChatOpenAI(
                openai_api_key=self.api_key,
                model_name=model_name,
                temperature=0.7
            )
        
        self.ingester = DocumentIngester()
        self.db = Database()
    
    def answer_question(self, question: str, employee_context: Dict = None) -> Dict:
        """Answer onboarding-related questions with citations."""
        # Query knowledge base
        kb_results = self.ingester.query_knowledge_base(question, n_results=5)
        
        # Build context from knowledge base results
        context = "\n\n".join([
            f"[Source: {r['metadata'].get('source', 'Unknown')}, Page {r['metadata'].get('page', 'N/A')}]\n{r['text']}"
            for r in kb_results
        ])
        
        # Build prompt
        employee_info = ""
        if employee_context:
            employee_info = f"\nEmployee Information:\n- Name: {employee_context.get('name', 'N/A')}\n- Role: {employee_context.get('role', 'N/A')}\n- Department: {employee_context.get('department', 'N/A')}\n"
        
        system_prompt = """You are an AI Employee Onboarding Assistant. Your role is to help new employees understand company policies, procedures, and their onboarding process. Always provide accurate, helpful answers based on the provided context. If the context doesn't contain enough information, say so clearly."""
        
        user_prompt = f"""Based on the following company documents and information, please answer this question: {question}

{employee_info}

Relevant Context from Company Documents:
{context if context else "No relevant context found in the knowledge base."}

Please provide a clear, comprehensive answer. At the end, list the sources you used (document names and page numbers)."""
        
        # Get response from LLM
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            answer = response.content if hasattr(response, 'content') else str(response)
        except AttributeError:
            # Fallback for older API
            response = self.llm(messages)
            answer = response.content if hasattr(response, 'content') else str(response)
        
        # Extract citations
        citations = []
        for result in kb_results:
            citations.append({
                'source': result['metadata'].get('source', 'Unknown'),
                'page': result['metadata'].get('page', 'N/A'),
                'relevance_score': 1 - result['distance'] if result['distance'] else None
            })
        
        return {
            'answer': answer,
            'citations': citations,
            'context_used': len(kb_results) > 0
        }
    
    def generate_onboarding_plan(self, employee_id: str, employee_data: Dict) -> Dict:
        """Generate a personalized onboarding plan for an employee."""
        # Query knowledge base for role-specific and general onboarding info
        role_query = f"onboarding process for {employee_data.get('role', 'employee')} in {employee_data.get('department', 'company')}"
        kb_results = self.ingester.query_knowledge_base(role_query, n_results=10)
        
        # Also get general onboarding info
        general_results = self.ingester.query_knowledge_base("employee onboarding checklist tasks", n_results=5)
        all_results = kb_results + general_results
        
        # Build context
        context = "\n\n".join([
            f"[Source: {r['metadata'].get('source', 'Unknown')}, Page {r['metadata'].get('page', 'N/A')}]\n{r['text']}"
            for r in all_results
        ])
        
        # Build prompt for plan generation
        system_prompt = """You are an AI Employee Onboarding Assistant specialized in creating personalized onboarding plans. Create comprehensive, structured onboarding plans that help new employees integrate smoothly into the company."""
        
        user_prompt = f"""Create a personalized onboarding plan for a new employee with the following information:

Employee Details:
- Name: {employee_data.get('name', 'N/A')}
- Role: {employee_data.get('role', 'N/A')}
- Department: {employee_data.get('department', 'N/A')}
- Start Date: {employee_data.get('start_date', 'N/A')}

Relevant Context from Company Documents:
{context if context else "General onboarding best practices."}

Please create a comprehensive onboarding plan that includes:
1. Week-by-week breakdown of activities
2. Specific tasks and milestones
3. Required training sessions
4. Key people to meet
5. Resources and documentation to review
6. Department-specific requirements

Format the response as a structured plan with clear phases (Week 1, Week 2, etc.) and actionable tasks."""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            response = self.llm.invoke(messages)
            plan_text = response.content if hasattr(response, 'content') else str(response)
        except AttributeError:
            # Fallback for older API
            response = self.llm(messages)
            plan_text = response.content if hasattr(response, 'content') else str(response)
        
        # Parse plan into structured format
        plan_data = self._parse_plan(plan_text)
        
        # Generate checklist items
        checklist_items = self._extract_checklist_items(plan_data)
        
        # Save to database
        plan_id = self.db.save_onboarding_plan(employee_id, plan_data, checklist_items)
        
        # Add tasks to progress tracking
        for item in checklist_items:
            self.db.add_progress_task(
                employee_id=employee_id,
                task_id=item.get('id', f"task_{len(checklist_items)}"),
                task_name=item.get('task', ''),
                status='pending'
            )
        
        return {
            'plan_id': plan_id,
            'plan_data': plan_data,
            'checklist_items': checklist_items,
            'full_plan_text': plan_text
        }
    
    def _parse_plan(self, plan_text: str) -> Dict:
        """Parse plan text into structured format."""
        # Simple parsing - can be enhanced with more sophisticated parsing
        plan_data = {
            'overview': plan_text[:500] if len(plan_text) > 500 else plan_text,
            'phases': [],
            'timeline': 'custom'
        }
        
        # Try to extract phases/weeks
        lines = plan_text.split('\n')
        current_phase = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if it's a phase header (Week 1, Phase 1, etc.)
            if any(keyword in line.lower() for keyword in ['week', 'phase', 'day', 'month']):
                if current_phase:
                    plan_data['phases'].append(current_phase)
                current_phase = {
                    'title': line,
                    'tasks': []
                }
            elif current_phase and (line.startswith('-') or line.startswith('•') or line[0].isdigit()):
                current_phase['tasks'].append(line.lstrip('- •0123456789. '))
        
        if current_phase:
            plan_data['phases'].append(current_phase)
        
        return plan_data
    
    def _extract_checklist_items(self, plan_data: Dict) -> List[Dict]:
        """Extract checklist items from plan data."""
        checklist = []
        task_id = 1
        
        for phase in plan_data.get('phases', []):
            for task in phase.get('tasks', []):
                checklist.append({
                    'id': f"task_{task_id}",
                    'phase': phase.get('title', 'General'),
                    'task': task,
                    'status': 'pending'
                })
                task_id += 1
        
        # If no phases found, create general checklist
        if not checklist:
            checklist.append({
                'id': 'task_1',
                'phase': 'General',
                'task': 'Review onboarding plan',
                'status': 'pending'
            })
        
        return checklist
    
    def generate_checklist(self, employee_id: str) -> List[Dict]:
        """Generate or retrieve checklist for an employee."""
        plan = self.db.get_onboarding_plan(employee_id)
        if plan:
            return plan['checklist_items']
        
        # If no plan exists, create a basic checklist
        employee = self.db.get_employee(employee_id)
        if employee:
            plan_data = self.generate_onboarding_plan(employee_id, employee)
            return plan_data['checklist_items']
        
        return []

