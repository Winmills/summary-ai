from langchain.chat_models import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain import PromptTemplate

llm = ChatOpenAI(temperature=0,model_name='gpt-3.5-turbo-16k')

prompt_template = """You are a helpful assistant that summarizes text. Break down the content into groups by main points and give me a explaination of the main points. 
Teach me on the main points using the content and some of your own knowledge

{text}
"""

PROMPT = PromptTemplate(template=prompt_template,input_variables=['text'])

refine_template = (
    "Your job is to product a final summary\n"
    "We have provided an existing summary up to a certain point: {existing_answer} \n"
    "refine the summary (only if needed) with some more content below. \n"
    "--------------\n"
    "{text}\n"
    "--------------\n"
    "Given the new context, refine the original summary"
    "If the context is new add to the summary, focus on the main points of the text"
    "Teach me on the main points using the content and some of your own knowledge"
)

refine_prompt = PromptTemplate(template=refine_template,input_variables=['text'])
chain = load_summarize_chain(llm,
                             chain_type='refine',
                             question_prompt=PROMPT,
                             refine_prompt=refine_prompt)
