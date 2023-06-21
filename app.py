import streamlit as st
import openai
import os
from ebooklib import epub
import base64
import requests

st.title("gpt-author")

st.markdown("By Matt Shumer ([https://twitter.com/mattshumer_](https://twitter.com/mattshumer_))")
st.markdown("Github repo: [https://github.com/mshumer/gpt-author](https://github.com/mshumer/gpt-author)")
st.markdown("Generate an entire novel in minutes, and automatically package it as an e-book.")

st.markdown("To generate a book:")
st.markdown("1. In the first cell, add in your OpenAI and Stability keys (see the first cell for instructions to get them).")
st.markdown("2. Fill in the prompt, number of chapters, and writing style in the last cell.")
st.markdown("3. Run all the cells! After some time, your EPUB file should appear in the filesystem.")

st.markdown("---")

st.markdown("# Setup")
st.code("""
!pip install openai
!pip install EbookLib

import openai
import os
from ebooklib import epub
import base64
import requests

openai.api_key = "ENTER OPENAI KEY HERE" # get it at https://platform.openai.com/
stability_api_key = "ENTER STABILITY KEY HERE" # get it at https://beta.dreamstudio.ai/
""")

st.markdown("# Functions")
st.code("""
def generate_cover_prompt(plot):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "You are a creative assistant that writes a spec for the cover art of a book, based on the book's plot."},
            {"role": "user", "content": f"Plot: {plot}\n\n--\n\nDescribe the cover we should create, based on the plot. This should be two sentences long, maximum."}
        ]
    )
    return response['choices'][0]['message']['content']

def create_cover_image(plot):
    plot = str(generate_cover_prompt(plot))
    engine_id = "stable-diffusion-xl-beta-v2-2-2"
    api_host = os.getenv('API_HOST', 'https://api.stability.ai')
    api_key = stability_api_key

    if api_key is None:
        raise Exception("Missing Stability API key.")

    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "text_prompts": [
                {
                    "text": plot
                }
            ],
            "cfg_scale": 7,
            "clip_guidance_preset": "FAST_BLUE",
            "height": 768,
            "width": 512,
            "samples": 1,
            "steps": 30,
        },
    )

    if response.status_code != 200:
        raise Exception("Non-200 response: " + str(response.text))

    data = response.json()

    for i, image in enumerate(data["artifacts"]):
        with open(f"/content/cover.png", "wb") as f: # replace this if running locally, to where you store the cover file
            f.write(base64.b64decode(image["base64"]))

def create_epub(title, author, chapters, cover_image_path='cover.png'):
    book = epub…
        "          steps_per_100_tokens=5,\n",
        "          max_tokens=4096,\n",
        "      )\n",
        "\n",
        "    print_step_costs(response, \"gpt-4-0613\")\n",
        "\n",
        "    return response['choices'][0]['message']['content']\n",
        "\n",
        "def generate_novel(prompt, num_chapters, writing_style):\n",
        "    plot = generate_plots(prompt)\n",
        "    final_plot = select_most_engaging(plot)\n",
        "    final_plot = improve_plot(final_plot)\n",
        "    title = get_title(final_plot)\n",
        "    chapters = [{\"Chapter 1\": write_first_chapter(final_plot, \"Chapter 1\", writing_style)}]\n",
        "\n",
        "    for i in range(1, num_chapters):\n",
        "        chapter_number = i + 1\n",
        "        chapter_title = f\"Chapter {chapter_number}\"\n",
        "        chapter_content = write_chapter(final_plot, chapter_title, writing_style)\n",
        "        chapters.append({chapter_title: chapter_content})\n",
        "\n",
        "    create_epub(title, author, chapters)\n",
        "\n",
        "\n",
        "prompt = \"In a world where magic is real and wizards rule, a young orphan named Sam discovers a hidden power within themselves. Sam must navigate a treacherous journey filled with danger and intrigue to uncover the truth about their past and save their world from destruction.\"\n",
        "num_chapters = 10\n",
        "writing_style = 'in the style of J.K. Rowling'\n",
        "author = 'Matt Shumer'\n",
        "\n",
        "generate_novel(prompt, num_chapters, writing_style)"
      ],
      "metadata": {
        "id": "1DUNIvTJH8uA"
      },
      "execution_count": null,
      "outputs": []
    }
  ]
}
