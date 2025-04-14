import gradio as gr
from dotenv import load_dotenv

from gradio_app.constants import EXAMPLE_QUERY
from gradio_app.travel_mapper import TravelMapperForUI
from gradio_app.utils import generate_generic_leafmap

load_dotenv()


def main():
    travel_mapper = TravelMapperForUI()

    # build the UI in gradio
    app = gr.Blocks()

    # make a generic map to display when the app first loads
    generic_map = generate_generic_leafmap()

    with app:
        gr.Markdown("## Generate travel suggestions")

        # make multple tabs
        with gr.Tabs():
            # make the first tab
            with gr.TabItem("Generate with map"):
                # make rows 1 within tab 1
                with gr.Row():
                    # make column 1 within row 1
                    with gr.Column():
                        text_input_map = gr.Textbox(
                            EXAMPLE_QUERY, label="Travel query", lines=4
                        )

                        query_validation_text = gr.Textbox(
                            label="Query validation information", lines=2
                        )

                    # make column 2 within row 1
                    with gr.Column():
                        # place where the map will appear
                        map_output = gr.HTML(generic_map, label="Travel map")
                        # place where the suggested trip will appear
                        itinerary_output = gr.Textbox(
                            value="Your itinerary will appear here",
                            label="Itinerary suggestion",
                            lines=3,
                        )
                map_button = gr.Button("Generate")

            # make the second tab
            with gr.TabItem("Generate without map"):
                # make the first row within the second tab
                with gr.Row():
                    # make the first column within the first row
                    with gr.Column():
                        text_input_no_map = gr.Textbox(
                            value=EXAMPLE_QUERY, label="Travel query", lines=3
                        )

                        query_validation_no_map = gr.Textbox(
                            label="Query validation information", lines=2
                        )
                    # make the second column within the first row
                    with gr.Column():
                        text_output_no_map = gr.Textbox(
                            value="Your itinerary will appear here",
                            label="Itinerary suggestion",
                            lines=3,
                        )
                text_button = gr.Button("Generate")

        map_button.click(
            travel_mapper.generate_with_leafmap,
            inputs=[text_input_map],
            outputs=[map_output, itinerary_output, query_validation_text],
        )
        text_button.click(
            travel_mapper.generate_without_leafmap,
            inputs=[text_input_no_map],
            outputs=[text_output_no_map, query_validation_no_map],
        )

    app.launch()


if __name__ == "__main__":
    main()
