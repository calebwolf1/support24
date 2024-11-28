from openai import OpenAI
import os
from dotenv import load_dotenv
import json

def parse_claim(text):
    # Load environmental variables
    load_dotenv()

    # Define prompt (big!)
    prompt = f"""Identify the concrete claims made in the following text that are posed as facts. 
            Some examples of concrete claims include: "The economy has improved drastically since 
            2008", "Inflation has increased by 15% since Trump's presidency", "The sky is red", "The 
            retail price of Air Jordans is $15". Be sure not to include opinions or hypotheticals such 
            as: "America is the best country", "Abortion should be illegal", “Gas should be cheaper”, 
            “If Trump wins, Russia would win the war”. With each claim, also include the exact piece 
            of text where the claim is from. Your output should be JSON and match the provided example.

            Example input with output:
            Input:
            THE VICE PRESIDENT:  But — but just as a point of emphasis on this important point: 
            Understand that this is an individual, Donald Trump, who is easily manipulated by flattery, 
            and we’ve seen that.  We’ve — don’t forget he — he dared to even consider vi- — inviting 
            the Taliban to Camp David.  Remember all this.  The love letters with Kim Jong Un.
            Let’s remember what we just most recently — what was reported.  During the height of COVID, 
            Americans were dying by the hundreds a day.  Nobody could get their hands on COVID tests.  
            You remember what that was.  During that time, he secretly sent COVID tests to Vladimir 
            Putin for his personal use. On the issue of Ukraine, he says, “Oh, well, I’d solve that 
            in a day.”  Well, I don’t think we as Americans think that the president of the United 
            States should solve an issue like that through surrender, and understand that’s what would 
            happen.  (Applause.)  Understand that’s what would happen.  Vladimir Putin would be sitting 
            in Kyiv if Donald Trump were president. 

            Output:
            {{
            "claims”: [
                {{
                    “claim”: “Donald Trump considered inviting the Taliban to Camp David”,
                    “source_text”: “he dared to even consider vi- — inviting the Taliban to Camp David”
                }},
                {{
                    “claim”: “Donald Trump exchanged love letters with Kim Jong Un”,
                    “source_text”: “The love letters with Kim Jong Un.”
                }},
                {{
                    “claim”: “During the height of COVID, Americans were dying by the hundreds a day”,
                    “source_text”: “During the height of COVID, Americans were dying by the hundreds a day.”
                }},
                {{
                    “claim”: “Donald Trump secretly sent COVID tests to Vladimir Putin for his personal use”,
                    “source_text”: “he secretly sent COVID tests to Vladimir Putin for his personal use.”
                }},
                {{
                    “claim”: “Donald Trump says he’d solve the issue of Ukraine in a day”,
                    “source_text”: “On the issue of Ukraine, he says, ‘Oh, well, I’d solve that in a day.’”
                }}
                ]
            }}

            Here is the text:
            {text}
            """
    
    # Instantiate the OpenAI client
    client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
        )

    # Call the OpeanAI api to get response
    completion = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[{"role": "user", "content": prompt}],
        )
    
    # Return the response
    return json.loads(completion.choices[0].message.content)



if __name__ == "__main__":
    text = """So, I want to address tonight a topic that is on everyone’s mind –the U.S. election. For those of us dedicated to climate action, last week’s outcome in the United States is obviously bitterly disappointing, particularly because of the unprecedented resources and ambition President Biden and Vice President Harris brought to the climate fight. Starting with our bold 2030 NDC to cut emissions by 50 to 52 percent below 2005 levels. By rejoining Paris. By making the largest investment in climate and clean energy in history through the Inflation Reduction Act and the Bipartisan Infrastructure Law. The President’s commitment to quadruple international climate funds from the United States to $11 billion per year. It’s clear that the next Administration will try to take a U turn and reverse much of this progress. Of course, I am keenly aware of the disappointment that the United States has at times caused the parties of the climate regime, who have lived through a pattern of strong, engaged, effective U.S. leadership, followed by sudden disengagement after a U.S. presidential election."""
    print(parse_claim(text))
