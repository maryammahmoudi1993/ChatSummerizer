from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv

from models import ChatMessage, SummaryResponse, Role
from memory_client import MemoryClient

# Load environment variables
load_dotenv()


class ChatSummarizer:
    """Chat summarization using LangChain and OpenAI"""
    
    def __init__(self):
        """Initialize the summarizer with OpenAI LLM"""
        self.llm = None
        self.redis_client = MemoryClient()
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the OpenAI LLM"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                print("Warning: OPENAI_API_KEY not found in environment variables")
                return
            
            self.llm = OpenAI(
                temperature=0.3,
                max_tokens=1000,
                openai_api_key=api_key
            )
            print("OpenAI LLM initialized successfully")
        except Exception as e:
            print(f"Error initializing OpenAI LLM: {e}")
            self.llm = None
    
    def _format_chat_for_summary(self, messages: List[ChatMessage]) -> str:
        """Format chat messages for summarization"""
        if not messages:
            return ""
        
        formatted_chat = []
        for message in messages:
            role = "User" if message.role == Role.USER else "Assistant"
            timestamp = message.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            
            # Add sentiment and topic if available
            sentiment_info = f" [Sentiment: {message.sentiment.value}]" if message.sentiment else ""
            topic_info = f" [Topic: {message.topic.value}]" if message.topic else ""
            
            formatted_chat.append(
                f"[{timestamp}] {role}{sentiment_info}{topic_info}: {message.content}"
            )
        
        return "\n".join(formatted_chat)
    
    def _create_summary_prompt(self) -> PromptTemplate:
        """Create a custom prompt template for chat summarization"""
        template = """
        You are an expert at summarizing chat conversations. Please provide a comprehensive summary of the following chat conversation.
        
        The summary should include:
        1. Main topics discussed
        2. Key decisions or conclusions reached
        3. Important questions asked and answers provided
        4. Overall sentiment of the conversation
        5. Any action items or next steps mentioned
        
        Chat Conversation:
        {text}
        
        Summary (max {max_length} words):
        """
        
        return PromptTemplate(
            input_variables=["text", "max_length"],
            template=template
        )
    
    def generate_summary(self, session_id: str, max_length: int = 500) -> SummaryResponse:
        """Generate a summary for a chat session"""
        if not self.llm:
            return SummaryResponse(
                session_id=session_id,
                summary="Error: OpenAI LLM not initialized. Please check your API key.",
                message_count=0
            )
        
        try:
            # Get messages from Redis
            messages = self.redis_client.get_session_messages(session_id)
            if not messages:
                return SummaryResponse(
                    session_id=session_id,
                    summary="No messages found for this session.",
                    message_count=0
                )
            
            # Format chat for summarization
            chat_text = self._format_chat_for_summary(messages)
            
            # Create summary chain
            prompt = self._create_summary_prompt()
            summary_chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Generate summary
            summary_result = summary_chain.run({
                "text": chat_text,
                "max_length": max_length
            })
            
            return SummaryResponse(
                session_id=session_id,
                summary=summary_result.strip(),
                message_count=len(messages)
            )
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return SummaryResponse(
                session_id=session_id,
                summary=f"Error generating summary: {str(e)}",
                message_count=0
            )
    
    def generate_brief_summary(self, session_id: str) -> str:
        """Generate a brief summary (1-2 sentences)"""
        try:
            messages = self.redis_client.get_session_messages(session_id)
            if not messages:
                return "No messages in this session."
            
            # Create a brief summary prompt
            brief_template = """
            Provide a brief 1-2 sentence summary of this chat conversation:
            
            {text}
            
            Brief summary:
            """
            
            prompt = PromptTemplate(
                input_variables=["text"],
                template=brief_template
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            chat_text = self._format_chat_for_summary(messages)
            
            result = chain.run({"text": chat_text})
            return result.strip()
            
        except Exception as e:
            print(f"Error generating brief summary: {e}")
            return "Error generating summary."
    
    def generate_structured_summary(self, session_id: str) -> Dict[str, Any]:
        """Generate a structured summary with key insights"""
        try:
            messages = self.redis_client.get_session_messages(session_id)
            if not messages:
                return {"error": "No messages found"}
            
            # Create structured summary prompt
            structured_template = """
            Analyze this chat conversation and provide a structured summary in JSON format with the following fields:
            - main_topics: List of main topics discussed
            - key_decisions: List of key decisions or conclusions
            - questions_asked: List of important questions
            - overall_sentiment: Overall sentiment (positive/negative/neutral)
            - action_items: List of action items or next steps
            - participant_count: Number of participants
            - conversation_duration: Approximate duration
            
            Chat:
            {text}
            
            JSON Summary:
            """
            
            prompt = PromptTemplate(
                input_variables=["text"],
                template=structured_template
            )
            
            chain = LLMChain(llm=self.llm, prompt=prompt)
            chat_text = self._format_chat_for_summary(messages)
            
            result = chain.run({"text": chat_text})
            
            # Try to parse JSON from result
            import json
            try:
                # Extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', result, re.DOTALL)
                if json_match:
                    structured_summary = json.loads(json_match.group())
                else:
                    structured_summary = {"raw_summary": result}
            except json.JSONDecodeError:
                structured_summary = {"raw_summary": result}
            
            return structured_summary
            
        except Exception as e:
            print(f"Error generating structured summary: {e}")
            return {"error": str(e)}
    
    def summarize_multiple_sessions(self, session_ids: List[str]) -> Dict[str, SummaryResponse]:
        """Summarize multiple chat sessions"""
        summaries = {}
        
        for session_id in session_ids:
            summary = self.generate_summary(session_id)
            summaries[session_id] = summary
        
        return summaries
    
    def health_check(self) -> bool:
        """Check if summarizer is working"""
        try:
            if not self.llm:
                return False
            
            # Test with a simple prompt
            test_prompt = PromptTemplate(
                input_variables=["text"],
                template="Summarize this text in one sentence: {text}"
            )
            
            chain = LLMChain(llm=self.llm, prompt=test_prompt)
            result = chain.run({"text": "Hello world"})
            
            return len(result.strip()) > 0
            
        except Exception as e:
            print(f"Summarizer health check failed: {e}")
            return False


# Global summarizer instance
chat_summarizer = ChatSummarizer() 