import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import numpy as np

class BaseballDashboard:
    def __init__(self, csv_file_path):
        self.df = pd.read_csv(csv_file_path)
        self.app = dash.Dash(__name__)
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        # Get unique players for dropdown
        players = sorted(self.df['Player'].unique()) if 'Player' in self.df.columns else sorted(self.df.index)
        
        self.app.layout = html.Div([
            html.H1("Baseball Player Analytics Dashboard", 
                   style={'textAlign': 'center', 'marginBottom': 30}),
            
            # Controls
            html.Div([
                html.Div([
                    html.Label("Select Player:"),
                    dcc.Dropdown(
                        id='player-dropdown',
                        options=[{'label': player, 'value': player} for player in players],
                        value=players[0] if players else None,
                        style={'width': '100%'}
                    )
                ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '3%'}),
                
                html.Div([
                    html.Label("Select Stats to Compare:"),
                    dcc.Dropdown(
                        id='stats-dropdown',
                        options=[
                            {'label': 'OBP', 'value': 'OBP'},
                            {'label': 'AVG', 'value': 'AVG'},
                            {'label': 'BABIP', 'value': 'BABIP'},
                            {'label': 'SLUG', 'value': 'SLUG'},
                            {'label': 'OPS', 'value': 'OPS'},
                            {'label': '2B', 'value': '2B'},
                            {'label': 'HR', 'value': 'HR'},
                            {'label': 'RBI', 'value': 'RBI'},
                            {'label': 'SB', 'value': 'SB'}
                        ],
                        value=['OBP', 'AVG', 'SLUG'],
                        multi=True,
                        style={'width': '100%'}
                    )
                ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '3%'}),
                
                html.Div([
                    html.Label("Season Filter:"),
                    dcc.RangeSlider(
                        id='season-slider',
                        min=self.df['Season'].min() if 'Season' in self.df.columns else 2020,
                        max=self.df['Season'].max() if 'Season' in self.df.columns else 2023,
                        value=[self.df['Season'].min() if 'Season' in self.df.columns else 2020,
                               self.df['Season'].max() if 'Season' in self.df.columns else 2023],
                        marks={i: str(i) for i in range(
                            self.df['Season'].min() if 'Season' in self.df.columns else 2020,
                            self.df['Season'].max() + 1 if 'Season' in self.df.columns else 2024
                        )},
                        step=1
                    )
                ], style={'width': '30%', 'display': 'inline-block'})
            ], style={'marginBottom': 30}),
            
            # Main content
            html.Div([
                # Player stats overview
                html.Div(id='player-stats-overview', style={'marginBottom': 20}),
                
                # Charts row 1
                html.Div([
                    html.Div([
                        dcc.Graph(id='batting-average-trend')
                    ], style={'width': '50%', 'display': 'inline-block'}),
                    
                    html.Div([
                        dcc.Graph(id='power-stats-chart')
                    ], style={'width': '50%', 'display': 'inline-block'})
                ]),
                
                # Charts row 2
                html.Div([
                    html.Div([
                        dcc.Graph(id='radar-chart')
                    ], style={'width': '50%', 'display': 'inline-block'}),
                    
                    html.Div([
                        dcc.Graph(id='comparison-chart')
                    ], style={'width': '50%', 'display': 'inline-block'})
                ]),
                
                # Charts row 3
                html.Div([
                    dcc.Graph(id='correlation-heatmap')
                ], style={'width': '100%'})
            ])
        ])
    
    def setup_callbacks(self):
        @self.app.callback(
            [Output('player-stats-overview', 'children'),
             Output('batting-average-trend', 'figure'),
             Output('power-stats-chart', 'figure'),
             Output('radar-chart', 'figure'),
             Output('comparison-chart', 'figure'),
             Output('correlation-heatmap', 'figure')],
            [Input('player-dropdown', 'value'),
             Input('stats-dropdown', 'value'),
             Input('season-slider', 'value')]
        )
        def update_dashboard(selected_player, selected_stats, season_range):
            # Filter data
            filtered_df = self.df.copy()
            if 'Season' in filtered_df.columns:
                filtered_df = filtered_df[
                    (filtered_df['Season'] >= season_range[0]) & 
                    (filtered_df['Season'] <= season_range[1])
                ]
            
            player_data = filtered_df[filtered_df['Player'] == selected_player] if 'Player' in filtered_df.columns else filtered_df
            
            # Player stats overview
            overview = self.create_stats_overview(player_data, selected_player)
            
            # Batting average trend
            trend_fig = self.create_batting_trend(player_data)
            
            # Power stats
            power_fig = self.create_power_stats(player_data)
            
            # Radar chart
            radar_fig = self.create_radar_chart(player_data, selected_stats)
            
            # Comparison chart
            comparison_fig = self.create_comparison_chart(filtered_df, selected_player, selected_stats)
            
            # Correlation heatmap
            heatmap_fig = self.create_correlation_heatmap(player_data)
            
            return overview, trend_fig, power_fig, radar_fig, comparison_fig, heatmap_fig
    
    def create_stats_overview(self, player_data, player_name):
        if player_data.empty:
            return html.Div("No data available for selected filters")
        
        latest_stats = player_data.iloc[-1] if len(player_data) > 0 else player_data.iloc[0]
        
        stats_cards = []
        key_stats = ['AVG', 'OBP', 'SLUG', 'OPS', 'HR', 'RBI']
        
        for stat in key_stats:
            if stat in latest_stats:
                stats_cards.append(
                    html.Div([
                        html.H3(f"{latest_stats[stat]:.3f}" if isinstance(latest_stats[stat], float) else str(latest_stats[stat])),
                        html.P(stat)
                    ], style={
                        'textAlign': 'center',
                        'backgroundColor': '#f8f9fa',
                        'padding': '20px',
                        'margin': '5px',
                        'borderRadius': '10px',
                        'width': '15%',
                        'display': 'inline-block'
                    })
                )
        
        return html.Div([
            html.H2(f"{player_name} - Latest Season Stats", style={'textAlign': 'center'}),
            html.Div(stats_cards, style={'textAlign': 'center'})
        ])
    
    def create_batting_trend(self, player_data):
        fig = go.Figure()
        
        if 'Season' in player_data.columns and len(player_data) > 1:
            for stat in ['AVG', 'OBP', 'SLUG']:
                if stat in player_data.columns:
                    fig.add_trace(go.Scatter(
                        x=player_data['Season'],
                        y=player_data[stat],
                        mode='lines+markers',
                        name=stat,
                        line=dict(width=3)
                    ))
        else:
            # If no season data, show single season comparison
            stats = ['AVG', 'OBP', 'SLUG']
            values = [player_data[stat].iloc[0] if stat in player_data.columns else 0 for stat in stats]
            fig.add_trace(go.Bar(x=stats, y=values, name='Current Stats'))
        
        fig.update_layout(
            title='Batting Statistics Trend',
            xaxis_title='Season' if 'Season' in player_data.columns else 'Statistics',
            yaxis_title='Value',
            hovermode='x unified'
        )
        
        return fig
    
    def create_power_stats(self, player_data):
        fig = make_subplots(rows=1, cols=2, subplot_titles=('Home Runs', 'Extra Base Hits'))
        
        if 'Season' in player_data.columns and len(player_data) > 1:
            # HR trend
            if 'HR' in player_data.columns:
                fig.add_trace(go.Bar(
                    x=player_data['Season'],
                    y=player_data['HR'],
                    name='HR',
                    marker_color='red'
                ), row=1, col=1)
            
            # Extra base hits
            extra_base = []
            for _, row in player_data.iterrows():
                xbh = 0
                if '2B' in row: xbh += row['2B'] if pd.notna(row['2B']) else 0
                if '3B' in row: xbh += row['3B'] if pd.notna(row['3B']) else 0
                if 'HR' in row: xbh += row['HR'] if pd.notna(row['HR']) else 0
                extra_base.append(xbh)
            
            fig.add_trace(go.Bar(
                x=player_data['Season'],
                y=extra_base,
                name='XBH',
                marker_color='blue'
            ), row=1, col=2)
        else:
            # Single season data
            hr_val = player_data['HR'].iloc[0] if 'HR' in player_data.columns else 0
            fig.add_trace(go.Bar(x=['HR'], y=[hr_val], marker_color='red'), row=1, col=1)
            
            xbh_val = 0
            if '2B' in player_data.columns: xbh_val += player_data['2B'].iloc[0] or 0
            if '3B' in player_data.columns: xbh_val += player_data['3B'].iloc[0] or 0
            if 'HR' in player_data.columns: xbh_val += player_data['HR'].iloc[0] or 0
            fig.add_trace(go.Bar(x=['XBH'], y=[xbh_val], marker_color='blue'), row=1, col=2)
        
        fig.update_layout(title_text="Power Statistics", showlegend=False)
        return fig
    
    def create_radar_chart(self, player_data, selected_stats):
        if player_data.empty:
            return go.Figure().add_annotation(text="No data available", showarrow=False)
        
        latest_data = player_data.iloc[-1]
        
        # Use selected stats or default ones
        radar_stats = selected_stats if selected_stats else ['AVG', 'OBP', 'SLUG', 'OPS']
        
        # Normalize values to 0-1 scale for radar chart
        values = []
        categories = []
        
        for stat in radar_stats:
            if stat in latest_data and pd.notna(latest_data[stat]):
                # Simple normalization - you might want to use league averages for better scaling
                if stat in ['AVG', 'OBP', 'SLUG', 'BABIP']:
                    normalized_val = min(latest_data[stat] / 0.400, 1.0)  # Scale batting stats
                elif stat == 'OPS':
                    normalized_val = min(latest_data[stat] / 1.000, 1.0)  # Scale OPS
                else:
                    # For counting stats, use a different normalization
                    normalized_val = min(latest_data[stat] / 50, 1.0)  # Adjust as needed
                
                values.append(normalized_val)
                categories.append(stat)
        
        if values:
            fig = go.Figure(data=go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name='Player Stats'
            ))
            
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1]
                    )),
                title="Player Performance Radar",
                showlegend=True
            )
        else:
            fig = go.Figure().add_annotation(text="No valid stats for radar chart", showarrow=False)
        
        return fig
    
    def create_comparison_chart(self, full_df, selected_player, selected_stats):
        if not selected_stats:
            return go.Figure().add_annotation(text="Select stats to compare", showarrow=False)
        
        # Get league averages
        league_avg = full_df[selected_stats].mean()
        player_data = full_df[full_df['Player'] == selected_player] if 'Player' in full_df.columns else full_df
        player_avg = player_data[selected_stats].mean()
        
        fig = go.Figure(data=[
            go.Bar(name='League Average', x=selected_stats, y=league_avg),
            go.Bar(name='Player Average', x=selected_stats, y=player_avg)
        ])
        
        fig.update_layout(
            title='Player vs League Comparison',
            barmode='group',
            xaxis_title='Statistics',
            yaxis_title='Value'
        )
        
        return fig
    
    def create_correlation_heatmap(self, player_data):
        numeric_columns = player_data.select_dtypes(include=[np.number]).columns
        correlation_data = player_data[numeric_columns].corr()
        
        fig = px.imshow(
            correlation_data,
            title="Statistics Correlation Heatmap",
            color_continuous_scale='RdBu',
            aspect='auto'
        )
        
        return fig
    
    def run(self, debug=True, port=8050):
        self.app.run_server(debug=debug, port=port)

# Sample data generator for testing
def generate_sample_data():
    """Generate sample baseball data for testing"""
    import random
    
    players = ['Mike Trout', 'Mookie Betts', 'Juan Soto', 'Aaron Judge', 'Vladimir Guerrero Jr.']
    seasons = [2021, 2022, 2023]
    
    data = []
    for player in players:
        for season in seasons:
            data.append({
                'Player': player,
                'Season': season,
                'AVG': round(random.uniform(0.250, 0.350), 3),
                'OBP': round(random.uniform(0.300, 0.450), 3),
                'SLUG': round(random.uniform(0.400, 0.650), 3),
                'OPS': round(random.uniform(0.700, 1.100), 3),
                'BABIP': round(random.uniform(0.250, 0.400), 3),
                'HR': random.randint(15, 50),
                '2B': random.randint(20, 45),
                '3B': random.randint(0, 8),
                'RBI': random.randint(60, 130),
                'SB': random.randint(0, 25),
                'BB': random.randint(40, 120),
                'SO': random.randint(80, 200)
            })
    
    df = pd.DataFrame(data)
    df['OPS'] = df['OBP'] + df['SLUG']  # Recalculate OPS to be accurate
    return df

# Usage example
if __name__ == "__main__":
    # Option 1: Use your own CSV file
    # dashboard = BaseballDashboard('your_baseball_data.csv')
    
    # Option 2: Generate sample data for testing
    sample_data = generate_sample_data()
    sample_data.to_csv('sample_baseball_data.csv', index=False)
    
    dashboard = BaseballDashboard('sample_baseball_data.csv')
    
    print("Starting Baseball Dashboard...")
    print("Open your browser and go to: http://127.0.0.1:8050")
    dashboard.run()