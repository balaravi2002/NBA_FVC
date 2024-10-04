from shiny import App, render, ui, reactive
import pandas as pd
import statsmodels.api as sm

# TABLES
df = pd.read_csv('NBA_FVC - NBA_FVC_2.0.csv')
playerlist = df["Player"].unique().tolist()
df_2024 = df[df["Start"] == 2024]
teamlist_abbr_2024 = df_2024["Team_Signed_With"].unique().tolist()

# TEAM Information /////////////////////////////////////////////////////
team_abbr_to_name = {
    'ATL': 'Atlanta Hawks',
    'BOS': 'Boston Celtics',
    'BKN': 'Brooklyn Nets',
    'CHA': 'Charlotte Hornets',
    'CHI': 'Chicago Bulls',
    'CLE': 'Cleveland Cavaliers',
    'DAL': 'Dallas Mavericks',
    'DEN': 'Denver Nuggets',
    'DET': 'Detroit Pistons',
    'GSW': 'Golden State Warriors',
    'HOU': 'Houston Rockets',
    'IND': 'Indiana Pacers',
    'LAC': 'Los Angeles Clippers',
    'LAL': 'Los Angeles Lakers',
    'MEM': 'Memphis Grizzlies',
    'MIA': 'Miami Heat',
    'MIL': 'Milwaukee Bucks',
    'MIN': 'Minnesota Timberwolves',
    'NOP': 'New Orleans Pelicans',
    'NYK': 'New York Knicks',
    'OKC': 'Oklahoma City Thunder',
    'ORL': 'Orlando Magic',
    'PHI': 'Philadelphia 76ers',
    'PHX': 'Phoenix Suns',
    'POR': 'Portland Trail Blazers',
    'SAC': 'Sacramento Kings',
    'SAS': 'San Antonio Spurs',
    'TOR': 'Toronto Raptors',
    'UTA': 'Utah Jazz',
    'WAS': 'Washington Wizards',
}

def get_full_team_name(abbr):
    return team_abbr_to_name.get(abbr, abbr)

teamlist_full_2024 = [get_full_team_name(abbr) for abbr in teamlist_abbr_2024]
#//////////////////////////////////////////////////////////////////////

# Custom CSS for additional styling
custom_css = """
    <style>
    .player-autocomplete div {
        margin-bottom: 5px;
    }
    .sidebar-like {
        margin-bottom: 20px;
    }
    .autocomplete-box {
        border: none;  /* Removes unwanted box */
        padding: 0;    /* Removes extra space */
    }
    </style>
"""

# UI
def app_ui(request=None):
    return ui.page_fluid(
        ui.h1("NBA Fair Value Calculator"),
        ui.head_content(ui.HTML(custom_css)),
        ui.navset_card_pill(
            # FIRST PAGE - Description
            ui.nav_panel(
                "NBA FVC Description",
                ui.p(
                    "Market value vs what they're actually paid. "
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis"
                    "nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore" 
                    "eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.",
                    style="font-size: 12px; font-family: Arial, sans-serif; color: #333;"
                )
            ),

            # SECOND PAGE - Player Dashboard
            ui.nav_panel(
                "Player Dashboard",
                ui.div(
                    ui.div(
                        ui.input_text("player_input", "Player:", ""),
                        ui.output_ui("player_autocomplete", style="margin-top: 0px;"),
                        class_="sidebar-like"
                    ),
                    ui.div(
                        ui.output_table("player_filtered"),
                        style="margin-top: 20px;"
                    ),
                    ui.div(
                        ui.output_text("regression_output"),
                        style="margin-top: 20px;"
                    )
                )
            ),

            # THIRD PAGE - Trade Machine
            ui.nav_panel(
                "Trade Machine",
                ui.row( 
                    ui.column(4,
                        ui.input_select("team_select", "Select Team 1:", choices=teamlist_full_2024),
                        ui.output_ui("player_dropdown_1"),
                        ui.output_text("player_info_1")
                    ),
                    ui.column(4,
                        ui.input_select("team_select_2", "Select Team 2:", choices=teamlist_full_2024),
                        ui.output_ui("player_dropdown_2"),
                        ui.output_text("player_info_2")
                    ),
                    ui.column(4,
                        ui.input_select("team_select_3", "Select Team 3:", choices=teamlist_full_2024),
                        ui.output_ui("player_dropdown_3"),
                        ui.output_text("player_info_3")
                    )
                )
            )    
        ),
        theme="https://stackpath.bootstrapcdn.com/bootswatch/4.5.2/lux/bootstrap.min.css"  
    )

# SERVER LOGIC
def server(input, output, session):

    # Reactive function to filter players based on the selected team for 2024 players
    @reactive.Calc
    def filtered_players(team_abbr):
        return df_2024[df_2024["Team Signed With"] == team_abbr]["Player"].tolist()

    # Render the player dropdown for Team 1
    @output
    @render.ui
    def player_dropdown_1():
        selected_team = input.team_select()
        team_abbr = {v: k for k, v in team_abbr_to_name.items()}.get(selected_team, selected_team)
        players = filtered_players(team_abbr)
        return ui.input_select("player_select_1", "Select a Player:", choices=players)

    # Render the player dropdown for Team 2
    @output
    @render.ui
    def player_dropdown_2():
        selected_team = input.team_select_2()
        team_abbr = {v: k for k, v in team_abbr_to_name.items()}.get(selected_team, selected_team)
        players = filtered_players(team_abbr)
        return ui.input_select("player_select_2", "Select a Player:", choices=players)

    # Render the player dropdown for Team 3
    @output
    @render.ui
    def player_dropdown_3():
        selected_team = input.team_select_3()
        team_abbr = {v: k for k, v in team_abbr_to_name.items()}.get(selected_team, selected_team)
        players = filtered_players(team_abbr)
        return ui.input_select("player_select_3", "Select a Player:", choices=players)

    # Display selected player's details for Team 1
    @output
    @render.text
    def player_info_1():
        selected_player = input.player_select_1()
        player_data = df_2024[df_2024["Player"] == selected_player]

        if player_data.empty:
            return "No data available for this player."

        # Extract relevant player details
        position = player_data["Pos"].values[0]
        contract_period = player_data["Contract Period"].values[0]
        years = player_data["Yrs"].values[0]
        age_at_start = player_data["Age_At_Start"].values[0]
        value = player_data["Value"].values[0]
        aav = player_data["AAV"].values[0]

        # Display the player details
        details = (
            f"Position: {position}\n"
            f"Contract Period: {contract_period}\n"
            f"Years: {years}\n"
            f"Age at Start: {age_at_start}\n"
            f"Value: {value}\n"
            f"AAV: {aav}"
        )

        return details

    # Function to handle the second team player dropdown
    @reactive.Calc
    def filtered_players_2():
        selected_team_2 = input.team_select_2()
        team_abbr_2 = {v: k for k, v in team_abbr_to_name.items()}.get(selected_team_2, selected_team_2)
        return df_2024[df_2024["Team Signed With"] == team_abbr_2]["Player"].tolist()

    @output
    @render.ui
    def player_dropdown_2():
        players_2 = filtered_players_2()
        return ui.input_select("player_select_2", "Select a Player:", choices=players_2)

    @output
    @render.text
    def player_info_2():
        selected_player_2 = input.player_select_2()
        player_data_2 = df_2024[df_2024["Player"] == selected_player_2]

        if player_data_2.empty:
            return "No data available for this player."

        # Extract relevant player details
        position_2 = player_data_2["Pos"].values[0]
        contract_period_2 = player_data_2["Contract Period"].values[0]
        years_2 = player_data_2["Yrs"].values[0]
        age_at_start_2 = player_data_2["Age_At_Start"].values[0]
        value_2 = player_data_2["Value"].values[0]
        aav_2 = player_data_2["AAV"].values[0]

        # Display the player details
        details_2 = (
            f"Position: {position_2}\n"
            f"Contract Period: {contract_period_2}\n"
            f"Years: {years_2}\n"
            f"Age at Start: {age_at_start_2}\n"
            f"Value: {value_2}\n"
            f"AAV: {aav_2}"
        )

        return details_2

    # Function to handle the third team player dropdown
    @reactive.Calc
    def filtered_players_3():
        selected_team_3 = input.team_select_3()
        if selected_team_3 is None or selected_team_3 == "":
            return []
        team_abbr_3 = {v: k for k, v in team_abbr_to_name.items()}.get(selected_team_3, selected_team_3)
        return df_2024[df_2024["Team Signed With"] == team_abbr_3]["Player"].tolist()

    @output
    @render.ui
    def player_dropdown_3():
        players_3 = filtered_players_3()
        return ui.input_select("player_select_3", "Select a Player:", choices=players_3)

    @output
    @render.text
    def player_info_3():
        selected_player_3 = input.player_select_3()
        if selected_player_3 is None or selected_player_3 == "":
            return "No data available for this player."

        player_data_3 = df_2024[df_2024["Player"] == selected_player_3]

        if player_data_3.empty:
            return "No data available for this player."

        # Extract relevant player details
        position_3 = player_data_3["Pos"].values[0]
        contract_period_3 = player_data_3["Contract Period"].values[0]
        years_3 = player_data_3["Yrs"].values[0]
        age_at_start_3 = player_data_3["Age_At_Start"].values[0]
        value_3 = player_data_3["Value"].values[0]
        aav_3 = player_data_3["AAV"].values[0]

        # Display the player details
        details_3 = (
            f"Position: {position_3}\n"
            f"Contract Period: {contract_period_3}\n"
            f"Years: {years_3}\n"
            f"Age at Start: {age_at_start_3}\n"
            f"Value: {value_3}\n"
            f"AAV: {aav_3}"
        )

        return details_3

    # Function to handle the fourth team player dropdown
    @reactive.Calc
    def filtered_players_4():
        selected_team_4 = input.team_select_4()
        if selected_team_4 is None or selected_team_4 == "":
            return []
        team_abbr_4 = {v: k for k, v in team_abbr_to_name.items()}.get(selected_team_4, selected_team_4)
        return df_2024[df_2024["Team Signed With"] == team_abbr_4]["Player"].tolist()

    @output
    @render.ui
    def player_dropdown_4():
        players_4 = filtered_players_4()
        return ui.input_select("player_select_4", "Select a Player:", choices=players_4)

    @output
    @render.text
    def player_info_4():
        selected_player_4 = input.player_select_4()
        if selected_player_4 is None or selected_player_4 == "":
            return "No data available for this player."

        player_data_4 = df_2024[df_2024["Player"] == selected_player_4]

        if player_data_4.empty:
            return "No data available for this player."

        # Extract relevant player details
        position_4 = player_data_4["Pos"].values[0]
        contract_period_4 = player_data_4["Contract Period"].values[0]
        years_4 = player_data_4["Yrs"].values[0]
        age_at_start_4 = player_data_4["Age_At_Start"].values[0]
        value_4 = player_data_4["Value"].values[0]
        aav_4 = player_data_4["AAV"].values[0]

        # Display the player details
        details_4 = (
            f"Position: {position_4}\n"
            f"Contract Period: {contract_period_4}\n"
            f"Years: {years_4}\n"
            f"Age at Start: {age_at_start_4}\n"
            f"Value: {value_4}\n"
            f"AAV: {aav_4}"
        )

        return details_4

# Create and run the app
app = App(app_ui, server)

if __name__ == "__main__":
    app.run()