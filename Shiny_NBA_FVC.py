from shiny import App, render, ui, reactive
import pandas as pd
import plotly.express as px
import sys

print(sys.version)

# Load your data
df = pd.read_csv('NBA_FVC - NBA_FVC_2.0.csv')

# Define your UI
def app_ui(request=None):
    return ui.page_fluid(
        ui.h1("NBA Player Analysis"),
        ui.div(
            ui.div(
                ui.input_select("player", "Select Player", df['Player'].unique().tolist()),
                ui.input_slider("year", "Select Year", min=df['Start'].min(), max=df['Start'].max(), value=df['Start'].max()),
                style="width: 30%; float: left;"
            ),
            ui.div(
                ui.h2("Player EPM Over Time"),
                ui.output_plot("epm_plot"),
                ui.h2("Player Stats"),
                ui.output_table("player_stats"),
                style="width: 70%; float: right;"
            ),
            style="display: flex;"
        )
    )

# Define your server logic
def server(input, output, session):
    @output
    @render.plot
    def epm_plot():
        player_data = df[df['Player'] == input.player()]
        fig = px.line(player_data, x='Start', y='EPM_1Y_Before', 
                      title=f"{input.player()}'s EPM (1 Year Before) Over Time")
        fig.add_scatter(x=player_data['Start'], y=player_data['EPM_2Y_Before'], 
                        mode='lines', name='EPM 2 Years Before')
        return fig

    @output
    @render.table
    def player_stats():
        player_data = df[(df['Player'] == input.player()) & (df['Start'] <= input.year())].iloc[-1]
        if not player_data.empty:
            return pd.DataFrame({
                "Stat": ["Age", "Position", "Team", "Contract Value", "Contract Years", "EPM (1Y Before)", "EPM (2Y Before)"],
                "Value": [
                    player_data['Age At Signing'],
                    player_data['Pos'],
                    player_data['Team Signed With'],
                    f"${player_data['Value']:,.0f}",
                    player_data['Yrs'],
                    f"{player_data['EPM_1Y_Before']:.2f}",
                    f"{player_data['EPM_2Y_Before']:.2f}"
                ]
            })
        else:
            return pd.DataFrame({"Stat": [], "Value": []})

# Create and run the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()