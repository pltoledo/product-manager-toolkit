import base64
import textwrap

import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st
import streamlit.components.v1 as components
from plotly.graph_objects import Figure

from skills import SKILLS


def wrap_text_for_plot(text: str) -> str:
    len_text = len(text)
    if len_text <= 40:
        return textwrap.fill(text, width=30).replace("\n", "<br>")
    else:
        return textwrap.fill(text, width=2 * len_text / 4).replace("\n", "<br>")


def st_auto_download(b64, file_name, mime_type):
    dl_link = f"""
            <html>
            <head>
            <title>Start Auto Download file</title>
            <script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>
            <script>
            $('<a href="data:{mime_type};base64,{b64}" download="{file_name}">')[0].click()
            </script>
            </head>
            </html>
            """
    components.html(dl_link)


class Home:
    def __init__(self) -> None:
        st.set_page_config(
            page_title="PM Toolkit Checklist",
            page_icon=":brain:",
        )

    def write_skill_widgets(self, skill_name: str, description: str) -> str:
        st.subheader(skill_name)
        st.write(description)
        return st.select_slider(
            skill_name,
            ("Precisa de Foco", "No Caminho", "Bem Desenvolvido"),
            label_visibility="hidden",
        )

    def write_skill_groups(
        self, skill_group_name: str, skill_group_items: dict[str, str]
    ) -> dict[str, str]:
        st.header(skill_group_name, divider="gray")
        st.write(skill_group_items["description"])
        skill_inputs = {}
        for skill in skill_group_items["items"]:
            skill_inputs[skill["name"]] = self.write_skill_widgets(
                skill["name"], skill["description"]
            )
        return skill_inputs

    def plot_radar(self, results: dict[str, str]) -> Figure:
        data = [(k, s, v) for k, skill_dict in results.items() for s, v in skill_dict.items()]
        df = pd.DataFrame(data, columns=["category", "skill", "label"])
        label_map = {"Precisa de Foco": 1, "No Caminho": 2, "Bem Desenvolvido": 3}
        df["value"] = df["label"].apply(lambda x: label_map[x])
        df["skill"] = df["skill"].apply(wrap_text_for_plot)
        fig = px.bar_polar(
            df,
            r="value",
            theta="skill",
            color="category",
            custom_data="label",
            color_discrete_map={
                "Execução do Produto": "#DB9B95",
                "Insights sobre o usuário": "#DBD3A4",
                "Estratégia do produto": "#9DDAB8",
                "Influenciando pessoas": "#A9A4DB",
            },
            start_angle=165,
        )
        fig.update_traces(hovertemplate="%{theta} <br> %{customdata[0]}<extra></extra>")
        fig.update_layout(
            height=600,
            width=500,
            margin=dict(t=0, b=100, r=0, l=0),
            polar_radialaxis_showline=False,
            polar_radialaxis_range=[1, 3],
            polar_radialaxis_showticklabels=False,
            polar_angularaxis_showgrid=False,
            polar_radialaxis_ticks="",
            legend=dict(
                title=None,
                orientation="h",
                xanchor="center",
                x=0.5,
                y=1.2,
                font=dict(size=14, color="black"),
            ),
            plot_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_traces(opacity=0.85)
        st.plotly_chart(fig, use_container_width=True)
        return fig

    def render(self):
        st.title("Product Manager Toolkit - Checklist")
        st.divider()
        st.write(
            """A partir do artigo [*How To Become a Peak Product Manager*](https://www.ravi-mehta.com/product-manager-skills/), do Ravi Mehta,
                 e do artigo recorte apresentado no curso de Product Manager da PM3 entitulado ***Qual é a sua forma? Guia do PM para o crescimento pessoal e da sua equipe***,
                construí esse app para facilitar a auto-avaliação de PMs nas skills apresentadas.
            """
        )
        st.write(
            "Basta preencher o questionário abaixo, e ao final será gerada a visualização apresentada nos artigos:"
        )
        with st.form("checklist"):
            results = {}
            for sklli_group_name, skill_group_items in SKILLS.items():
                results[sklli_group_name] = self.write_skill_groups(
                    sklli_group_name, skill_group_items
                )
            submit = st.form_submit_button("Enviar")
        st.divider()
        if submit:
            fig = self.plot_radar(results)
            img_bytes = pio.to_image(fig, width=1000, scale=2, format="png")
            img_b64 = base64.b64encode(img_bytes).decode()
            st_auto_download(img_b64, "pm_toolkit_plot.png", "image/png")
        cols = st.columns(10)
        cols[4].markdown(
            "[![Repo](https://img.icons8.com/material-outlined/48/000000/github.png)](https://github.com/pltoledo/product-manager-toolkit)"
        )
        cols[5].markdown(
            "[![linkedin](https://img.icons8.com/color/48/linkedin.png)](https://linkedin.com/in/pedro-toledo)"
        )


if __name__ == "__main__":
    Home().render()
