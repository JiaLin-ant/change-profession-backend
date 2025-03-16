from groq import Groq
import json
import os
import requests

# Initialize the Groq client 
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Define models
ROUTING_MODEL = "llama3-70b-8192"
TOOL_USE_MODEL = "llama-3.3-70b-versatile"
GENERAL_MODEL = "llama3-70b-8192"

def calculate(expression):
    """Tool to evaluate a mathematical expression"""
    try:
        result = eval(expression)
        return json.dumps({"result": result})
    except:
        return json.dumps({"error": "Invalid expression"})

def web_search(query):
    """Tool to perform a search using Wikipedia API"""
    try:
        # Wikipedia API endpoint
        base_url = "https://zh.wikipedia.org/w/api.php"  # 使用中文维基百科
        
        # First, search for relevant pages
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query,
            "srlimit": 3,  # Limit to top 3 results
            "utf8": 1
        }
        
        search_response = requests.get(base_url, params=search_params)
        if search_response.status_code != 200:
            return json.dumps({"error": f"Search failed with status code {search_response.status_code}"})
            
        search_data = search_response.json()
        if "query" not in search_data or "search" not in search_data["query"]:
            return json.dumps({"error": "No results found"})
            
        results = []
        for item in search_data["query"]["search"]:
            # Get detailed page content for each search result
            content_params = {
                "action": "query",
                "format": "json",
                "prop": "extracts|info",
                "exintro": True,  # Only get the introduction section
                "explaintext": True,  # Get plain text instead of HTML
                "inprop": "url",
                "pageids": item["pageid"],
                "utf8": 1
            }
            
            content_response = requests.get(base_url, params=content_params)
            if content_response.status_code == 200:
                content_data = content_response.json()
                page = list(content_data["query"]["pages"].values())[0]
                
                results.append({
                    "title": page.get("title", ""),
                    "snippet": page.get("extract", "")[:500] + "...",  # Limit snippet length
                    "link": page.get("fullurl", "")
                })
        
        return json.dumps({"results": results})
    except Exception as e:
        return json.dumps({"error": str(e)})

def route_query(query):
    """Routing logic to let LLM decide if tools are needed"""
    routing_prompt = f"""
    Given the following user query, determine if any tools are needed to answer it.
    
    Guidelines:
    1. If the query requires mathematical calculations, respond with 'TOOL: CALCULATE'
    2. If the query is asking about:
       - Factual information
       - Current events
       - Definitions
       - Technical concepts
       - General knowledge
       Then respond with 'TOOL: SEARCH'
    3. If the query is conversational or opinion-based with no need for external information, respond with 'NO TOOL'

    Examples:
    - "What is Python programming language?" -> 'TOOL: SEARCH' (requires factual information)
    - "Calculate 25 * 4 + 10" -> 'TOOL: CALCULATE' (requires calculation)
    - "How are you doing?" -> 'NO TOOL' (conversational)
    - "What is machine learning?" -> 'TOOL: SEARCH' (technical concept)
    - "Who won the latest Nobel Prize?" -> 'TOOL: SEARCH' (current events)

    User query: {query}

    Response:
    """
    
    response = client.chat.completions.create(
        model=ROUTING_MODEL,
        messages=[
            {"role": "system", "content": "You are a routing assistant. Your job is to determine if external tools are needed to accurately answer the user's query."},
            {"role": "user", "content": routing_prompt}
        ],
        max_completion_tokens=20  # We only need a short response
    )
    
    routing_decision = response.choices[0].message.content.strip()
    
    if "TOOL: CALCULATE" in routing_decision:
        return "calculate"
    elif "TOOL: SEARCH" in routing_decision:
        return "search"
    else:
        return "no tool needed"

def run_with_tool(query, tool_type):
    """Use the tool use model to perform the calculation or search"""
    messages = [
        {
            "role": "system",
            "content": """You are an assistant that can perform calculations and web searches. 
            When using search results, summarize the information in a clear and natural way.
            For calculations, show both the calculation and the result.
            Always respond in the same language as the user's query.
            DO NOT show the function call format in your response.""",
        },
        {
            "role": "user",
            "content": query,
        }
    ]
    
    # Define available tools
    if tool_type == "calculate":
        tools = [{
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Evaluate a mathematical expression",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "The mathematical expression to evaluate",
                        }
                    },
                    "required": ["expression"],
                },
            },
        }]
    else:  # search
        tools = [{
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Perform a web search query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to perform",
                        }
                    },
                    "required": ["query"],
                },
            },
        }]

    try:
        # First API call to get tool calls
        response = client.chat.completions.create(
            model=TOOL_USE_MODEL,
            messages=messages,
            tools=tools,
            tool_choice={"type": "function", "function": {"name": tools[0]["function"]["name"]}},
            max_completion_tokens=4096
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        if tool_calls:
            # Add the assistant's message with tool calls
            messages.append(response_message)
            
            # Process each tool call
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                # Execute the appropriate function
                if function_name == "calculate":
                    function_response = calculate(function_args.get("expression"))
                elif function_name == "web_search":
                    function_response = web_search(function_args.get("query"))
                
                # Parse the function response
                parsed_response = json.loads(function_response)
                
                # Add the function response to messages
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                })
            
            # Add a prompt to guide the final response
            messages.append({
                "role": "user",
                "content": """请根据上述工具返回的结果，用自然的语言回答我的问题。
                如果是搜索结果，请总结主要信息；如果是计算结果，请展示计算过程和结果。
                注意：请直接给出答案，不要显示函数调用的格式。"""
            })
            
            # Second API call to get the final response
            second_response = client.chat.completions.create(
                model=TOOL_USE_MODEL,
                messages=messages,
                max_completion_tokens=4096
            )
            
            return second_response.choices[0].message.content
        
        # If no tool calls were made, return the original response
        return response_message.content
        
    except Exception as e:
        return f"抱歉，处理您的请求时出现了错误: {str(e)}"

def run_general(query):
    """Use the general model to answer the query since no tool is needed"""
    response = client.chat.completions.create(
        model=GENERAL_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ]
    )
    return response.choices[0].message.content

def process_query(query):
    """Process the query and route it to the appropriate model"""
    route = route_query(query)
    if route in ["calculate", "search"]:
        response = run_with_tool(query, route)
    else:
        response = run_general(query)
    
    return {
        "query": query,
        "route": route,
        "response": response
    }

# Example usage
if __name__ == "__main__":
    # Test queries with different types of questions
    test_queries = [
        "中国的首都在哪里？",      # 地理知识查询
        "计算 123 + 456 * 789",    # 数学计算
        "Python是什么编程语言？",   # 技术概念查询
        "今天是几号？",   # 对话类
        "长城是什么时候建造的？"    # 历史知识查询
    ]
    
    for query in test_queries:
        print("\n" + "="*50)
        print(f"查询: {query}")
        result = process_query(query)
        print(f"路由: {result['route']}")
        print(f"回答: {result['response']}")
        print("="*50)