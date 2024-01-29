from openai import OpenAI
import json
import db_helper
client = OpenAI(api_key="YOUR API KEY")


def get_answer(question):

    messages = [{'role': 'user', 'content': question}]
    tools = [
    {
        "type": "function",
        "function": {
            "name": "get_marks",
            "description":"""Get the GPA for a college student or aggregate GPA (such as average, min, max) 
            for a given semester. If function returns -1 then it means we could not find the record in a database for given input. 
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "student_name": {
                        "type": "string",
                        "description": "First and last Name of the student. e.g John Smith",
                    },
                    "semester": {
                        "type": "integer",
                        "description": "A number between 1 to 4 indicating the semester of a student",
                    },
                    "operation": {
                        "type": "string",
                        "description": """If student is blank that means aggregate number such as max, min or average is being
                            requested for an entire semester. semester must be passed in this case. If student field is blank and say 
                            they are passing 1 as a value in semester. Then operation parameter will tell if they need a maximum, minimum
                            or an average GPA of all students in semester 1.
                            """,
                        "enum": ["max", "min", "avg"]
                    },
                },
                "required": ["semester"],
            },
    }
    },
        {
        "type": "function",
        "function": {
            "name": "get_fees",
            "description":"""Get the fees for an individual student or total fees for an entire 
            semester. If function returns -1 then it means we could not find the record in a database for given input.Currency is in US Dollars
            """,
            "parameters": {
                "type": "object",
                "properties": {
                    "student_name": {
                        "type": "string",
                        "description": "First and last Name of the student. e.g John Smith",
                    },
                    "semester": {
                        "type": "integer",
                        "description": "A number between 1 to 4 indicating the semester of a student",
                    },
                    "fees_type": {
                        "type": "string",
                        "description": "fee type such as 'paid', 'pending' or 'total'",
                        "enum": ["paid", "pending", "total"]
                    },
                },
                "required": ["semester"],
            },
    }
    }
    ]

    response = client.chat.completions.create(
    model="gpt-3.5-turbo-1106",
    messages=messages,
    tools=tools,
    tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        available_functions = {
            "get_marks": db_helper.get_marks,
            "get_fees": db_helper.get_fees
        }  # only one function in this example, but you can have multiple
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(
                function_args
                
            )
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
        )  # get a new response from the model where it can see the function response

        return second_response.choices[0].message.content
    

if __name__ == '__main__':
    print(get_answer("What was Peter Pandey's GPA in semester 1?"))
    print(get_answer("average gpa in third semester?"))
    print(get_answer("how much is peter pandey's pending fees in the first semester?"))
    print(get_answer("how much was peter pandey's due fees in the first semester?"))
    print(get_answer("what is the purpose of a balance sheet?"))
    