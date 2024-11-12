from shiny import App, ui, render, reactive
import folium
from geopy.geocoders import Nominatim

# User Interface
app_ui = ui.page_fluid(
    # Main title with blue background
    ui.h2("Real Estate Price Prediction Tool", style="background-color: #6180c2; color: white; padding: 10px; border-radius: 5px;"),
    ui.row(
        # Left column with bordered container for inputs
        ui.column(
            6,
            ui.div(
                ui.h3("Input", style="background-color: #6180c2; color: white; padding: 10px; border-radius: 5px 5px 0 0; margin: 0;"),
                ui.div(
                    ui.input_text("address_input", "Enter Address", ""),
                    ui.input_text("city", "Enter City", ""),
                    ui.input_text("state", "Enter State", ""),
                    ui.input_text("zip_code", "Enter Zipcode", ""),
                    ui.input_text_area("description_input", "Enter Description", ""),
                    ui.input_text_area("num_bedroom", "Enter Number of Bedrooms", ""),
                    ui.input_text_area("num_bathrooms", "Enter Number of Bathrooms", ""),
                    ui.input_action_button("show_map_btn", "Show on Map"),
                    style="background-color: white; border: 2px solid #6180c2; padding: 15px; border-radius: 0 0 5px 5px;"
                ),
            )
        ),
        # Right column with bordered container for output
        ui.column(
            6,
            ui.div(
                ui.h3("Output", style="background-color: #6180c2; color: white; padding: 10px; border-radius: 5px 5px 0 0; margin: 0;"),
                ui.div(
                    ui.h4("Map"),
                    ui.output_ui("map_output"),
                    ui.h4("Predicted Price:"),
                    ui.output_text_verbatim("score_output"),
                    style="background-color: white; border: 2px solid #6180c2; padding: 15px; border-radius: 0 0 5px 5px;"
                ),
            )
        ),
    ),
)

# Server function
def server(input, output, session):
    geolocator = Nominatim(user_agent="shiny_app")

    # Reactive value to store the coordinates
    location_coords = reactive.Value(None)

    @reactive.Effect
    @reactive.event(input.show_map_btn)
    def update_location():
        address = input.address_input()
        if address.strip() == "":
            location_coords.set(None)
            return

        try:
            location = geolocator.geocode(address)
            if location:
                # Update reactive value with new coordinates
                location_coords.set((location.latitude, location.longitude))
            else:
                location_coords.set(None)
        except Exception as e:
            location_coords.set(None)

    @output
    @render.ui
    def map_output():
        coords = location_coords.get()
        if coords is None:
            return ui.p("Enter a valid address and click 'Show on Map' to see the map.")
        else:
            # Create a Folium map centered at the input location
            m = folium.Map(location=coords, zoom_start=15)
            folium.Marker(coords, tooltip="Input Address").add_to(m)

            # Render the map to HTML
            map_html = m._repr_html_()

            # Return the HTML as a UI element
            return ui.HTML(map_html)

    @output
    @render.text
    def score_output():
        # Placeholder score calculation
        return "Price will be displayed here"

# Create the Shiny app
app = App(app_ui, server)