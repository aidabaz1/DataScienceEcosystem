{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "71488422-d1f5-4412-93c8-840588b60a34",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Import required libraries\n",
    "import pandas as pd\n",
    "import dash\n",
    "from dash import dcc\n",
    "from dash import html\n",
    "from dash.dependencies import Input, Output\n",
    "import plotly.graph_objs as go\n",
    "import plotly.express as px"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "d039ecb6-6717-4b50-9b1b-00e5b8a053f8",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Read the SpaceX launch data\n",
    "spacex_df = pd.read_csv(\"https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/dataset_part_1.csv\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "id": "2b225427-c7af-4a34-b41c-fa28f2c7a868",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Load the data\n",
    "spacex_df = pd.read_csv(\"https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv\")\n",
    "\n",
    "# Initialize the Dash app\n",
    "app = dash.Dash(__name__)\n",
    "\n",
    "# Get unique launch sites for dropdown\n",
    "launch_sites = spacex_df['Launch Site'].unique().tolist()\n",
    "dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + \\\n",
    "                  [{'label': site, 'value': site} for site in launch_sites]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "917be4d0-54c7-48b6-8f30-1dabdf86ef23",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Define the app layout\n",
    "app.layout = html.Div(children=[\n",
    "    html.H1('SpaceX Launch Records Dashboard',\n",
    "            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),\n",
    "    \n",
    "    # TASK 1: Dropdown for Launch Sites\n",
    "    dcc.Dropdown(\n",
    "        id='site-dropdown',\n",
    "        options=dropdown_options,\n",
    "        value='ALL',\n",
    "        placeholder=\"Select a Launch Site here\",\n",
    "        searchable=True\n",
    "    ),\n",
    "    \n",
    "    html.Br(),\n",
    "    \n",
    "    # Pie chart for success rates\n",
    "    html.Div(dcc.Graph(id='success-pie-chart')),\n",
    "    \n",
    "    html.Br(),\n",
    "    \n",
    "    # TASK 3: Range Slider for Payload\n",
    "    html.P(\"Payload range (Kg):\"),\n",
    "    dcc.RangeSlider(\n",
    "        id='payload-slider',\n",
    "        min=0,\n",
    "        max=10000,\n",
    "        step=1000,\n",
    "        marks={i: str(i) for i in range(0, 10001, 1000)},\n",
    "        value=[spacex_df['Payload Mass (kg)'].min(), spacex_df['Payload Mass (kg)'].max()]\n",
    "    ),\n",
    "    \n",
    "    html.Br(),\n",
    "    \n",
    "    # Scatter chart for payload vs success\n",
    "    html.Div(dcc.Graph(id='success-payload-scatter-chart')),\n",
    "])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "id": "672928f9-24e3-4e10-87f9-2a9376ea192e",
   "metadata": {},
   "outputs": [],
   "source": [
    "# TASK 2: Callback for Pie Chart\n",
    "@app.callback(\n",
    "    Output(component_id='success-pie-chart', component_property='figure'),\n",
    "    Input(component_id='site-dropdown', component_property='value')\n",
    ")\n",
    "def update_pie_chart(entered_site):\n",
    "    if entered_site == 'ALL':\n",
    "        # Total success count for all sites\n",
    "        fig = px.pie(\n",
    "            spacex_df, \n",
    "            names='Launch Site',\n",
    "            title='Total Success Launches By Site'\n",
    "        )\n",
    "    else:\n",
    "        # Filter data for selected site\n",
    "        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]\n",
    "        success_count = filtered_df['class'].sum()\n",
    "        failure_count = len(filtered_df) - success_count\n",
    "        \n",
    "        pie_data = pd.DataFrame({\n",
    "            'Outcome': ['Success', 'Failure'],\n",
    "            'Count': [success_count, failure_count]\n",
    "        })\n",
    "        \n",
    "        fig = px.pie(\n",
    "            pie_data,\n",
    "            values='Count',\n",
    "            names='Outcome',\n",
    "            title=f'Total Success Launches for site {entered_site}'\n",
    "        )\n",
    "    \n",
    "    return fig"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "ff6ea655-715d-46b3-9d78-e55d17c8cf32",
   "metadata": {},
   "outputs": [],
   "source": [
    "# TASK 4: Callback for Scatter Chart\n",
    "@app.callback(\n",
    "    Output(component_id='success-payload-scatter-chart', component_property='figure'),\n",
    "    [Input(component_id='site-dropdown', component_property='value'),\n",
    "     Input(component_id='payload-slider', component_property='value')]\n",
    ")\n",
    "def update_scatter_chart(entered_site, payload_range):\n",
    "    # Filter data based on payload range\n",
    "    low, high = payload_range\n",
    "    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & \n",
    "                           (spacex_df['Payload Mass (kg)'] <= high)]\n",
    "    \n",
    "    # Further filter by site if needed\n",
    "    if entered_site != 'ALL':\n",
    "        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]\n",
    "    \n",
    "    # Create scatter plot\n",
    "    fig = px.scatter(\n",
    "        filtered_df,\n",
    "        x='Payload Mass (kg)',\n",
    "        y='class',\n",
    "        color='Booster Version Category',\n",
    "        title='Correlation between Payload and Success for all Sites',\n",
    "        labels={'class': 'Launch Outcome (1=Success, 0=Failure)'}\n",
    "    )\n",
    "    \n",
    "    return fig"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "374b8b78-a394-43de-b79d-b9d5fff02f80",
   "metadata": {},
   "outputs": [
    {
     "ename": "OSError",
     "evalue": "Address 'http://127.0.0.1:8050' already in use.\n    Try passing a different port to run.",
     "output_type": "error",
     "traceback": [
      "\u001b[1;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[1;31mOSError\u001b[0m                                   Traceback (most recent call last)",
      "Cell \u001b[1;32mIn[8], line 3\u001b[0m\n\u001b[0;32m      1\u001b[0m \u001b[38;5;66;03m# Run the app\u001b[39;00m\n\u001b[0;32m      2\u001b[0m \u001b[38;5;28;01mif\u001b[39;00m \u001b[38;5;18m__name__\u001b[39m \u001b[38;5;241m==\u001b[39m \u001b[38;5;124m'\u001b[39m\u001b[38;5;124m__main__\u001b[39m\u001b[38;5;124m'\u001b[39m:\n\u001b[1;32m----> 3\u001b[0m     app\u001b[38;5;241m.\u001b[39mrun(host\u001b[38;5;241m=\u001b[39m\u001b[38;5;124m'\u001b[39m\u001b[38;5;124m127.0.0.1\u001b[39m\u001b[38;5;124m'\u001b[39m, port\u001b[38;5;241m=\u001b[39m\u001b[38;5;241m8050\u001b[39m, debug\u001b[38;5;241m=\u001b[39m\u001b[38;5;28;01mTrue\u001b[39;00m)\n",
      "File \u001b[1;32m~\\anaconda3\\Lib\\site-packages\\dash\\dash.py:2363\u001b[0m, in \u001b[0;36mDash.run\u001b[1;34m(self, host, port, proxy, debug, jupyter_mode, jupyter_width, jupyter_height, jupyter_server_url, dev_tools_ui, dev_tools_props_check, dev_tools_serve_dev_bundles, dev_tools_hot_reload, dev_tools_hot_reload_interval, dev_tools_hot_reload_watch_interval, dev_tools_hot_reload_max_retry, dev_tools_silence_routes_logging, dev_tools_disable_version_check, dev_tools_prune_errors, **flask_run_options)\u001b[0m\n\u001b[0;32m   2360\u001b[0m             extra_files\u001b[38;5;241m.\u001b[39mappend(path)\n\u001b[0;32m   2362\u001b[0m \u001b[38;5;28;01mif\u001b[39;00m jupyter_dash\u001b[38;5;241m.\u001b[39mactive:\n\u001b[1;32m-> 2363\u001b[0m     jupyter_dash\u001b[38;5;241m.\u001b[39mrun_app(\n\u001b[0;32m   2364\u001b[0m         \u001b[38;5;28mself\u001b[39m,\n\u001b[0;32m   2365\u001b[0m         mode\u001b[38;5;241m=\u001b[39mjupyter_mode,\n\u001b[0;32m   2366\u001b[0m         width\u001b[38;5;241m=\u001b[39mjupyter_width,\n\u001b[0;32m   2367\u001b[0m         height\u001b[38;5;241m=\u001b[39mjupyter_height,\n\u001b[0;32m   2368\u001b[0m         host\u001b[38;5;241m=\u001b[39mhost,\n\u001b[0;32m   2369\u001b[0m         port\u001b[38;5;241m=\u001b[39mport,\n\u001b[0;32m   2370\u001b[0m         server_url\u001b[38;5;241m=\u001b[39mjupyter_server_url,\n\u001b[0;32m   2371\u001b[0m     )\n\u001b[0;32m   2372\u001b[0m \u001b[38;5;28;01melse\u001b[39;00m:\n\u001b[0;32m   2373\u001b[0m     \u001b[38;5;28mself\u001b[39m\u001b[38;5;241m.\u001b[39mserver\u001b[38;5;241m.\u001b[39mrun(host\u001b[38;5;241m=\u001b[39mhost, port\u001b[38;5;241m=\u001b[39mport, debug\u001b[38;5;241m=\u001b[39mdebug, \u001b[38;5;241m*\u001b[39m\u001b[38;5;241m*\u001b[39mflask_run_options)\n",
      "File \u001b[1;32m~\\anaconda3\\Lib\\site-packages\\dash\\_jupyter.py:408\u001b[0m, in \u001b[0;36mJupyterDash.run_app\u001b[1;34m(self, app, mode, width, height, host, port, server_url)\u001b[0m\n\u001b[0;32m    406\u001b[0m     display(HTML(msg))\n\u001b[0;32m    407\u001b[0m \u001b[38;5;28;01melse\u001b[39;00m:\n\u001b[1;32m--> 408\u001b[0m     \u001b[38;5;28;01mraise\u001b[39;00m final_error\n",
      "File \u001b[1;32m~\\anaconda3\\Lib\\site-packages\\dash\\_jupyter.py:395\u001b[0m, in \u001b[0;36mJupyterDash.run_app\u001b[1;34m(self, app, mode, width, height, host, port, server_url)\u001b[0m\n\u001b[0;32m    392\u001b[0m         \u001b[38;5;28;01mraise\u001b[39;00m err\n\u001b[0;32m    394\u001b[0m \u001b[38;5;28;01mtry\u001b[39;00m:\n\u001b[1;32m--> 395\u001b[0m     wait_for_app()\n\u001b[0;32m    397\u001b[0m     \u001b[38;5;28;01mif\u001b[39;00m \u001b[38;5;28mself\u001b[39m\u001b[38;5;241m.\u001b[39min_colab:\n\u001b[0;32m    398\u001b[0m         JupyterDash\u001b[38;5;241m.\u001b[39m_display_in_colab(dashboard_url, port, mode, width, height)\n",
      "File \u001b[1;32m~\\anaconda3\\Lib\\site-packages\\retrying.py:55\u001b[0m, in \u001b[0;36mretry.<locals>.wrap.<locals>.wrapped_f\u001b[1;34m(*args, **kw)\u001b[0m\n\u001b[0;32m     53\u001b[0m \u001b[38;5;129m@wraps\u001b[39m(f)\n\u001b[0;32m     54\u001b[0m \u001b[38;5;28;01mdef\u001b[39;00m\u001b[38;5;250m \u001b[39m\u001b[38;5;21mwrapped_f\u001b[39m(\u001b[38;5;241m*\u001b[39margs, \u001b[38;5;241m*\u001b[39m\u001b[38;5;241m*\u001b[39mkw):\n\u001b[1;32m---> 55\u001b[0m     \u001b[38;5;28;01mreturn\u001b[39;00m Retrying(\u001b[38;5;241m*\u001b[39mdargs, \u001b[38;5;241m*\u001b[39m\u001b[38;5;241m*\u001b[39mdkw)\u001b[38;5;241m.\u001b[39mcall(f, \u001b[38;5;241m*\u001b[39margs, \u001b[38;5;241m*\u001b[39m\u001b[38;5;241m*\u001b[39mkw)\n",
      "File \u001b[1;32m~\\anaconda3\\Lib\\site-packages\\retrying.py:289\u001b[0m, in \u001b[0;36mRetrying.call\u001b[1;34m(self, fn, *args, **kwargs)\u001b[0m\n\u001b[0;32m    286\u001b[0m \u001b[38;5;28;01mif\u001b[39;00m \u001b[38;5;28mself\u001b[39m\u001b[38;5;241m.\u001b[39mstop(attempt_number, delay_since_first_attempt_ms):\n\u001b[0;32m    287\u001b[0m     \u001b[38;5;28;01mif\u001b[39;00m \u001b[38;5;129;01mnot\u001b[39;00m \u001b[38;5;28mself\u001b[39m\u001b[38;5;241m.\u001b[39m_wrap_exception \u001b[38;5;129;01mand\u001b[39;00m attempt\u001b[38;5;241m.\u001b[39mhas_exception:\n\u001b[0;32m    288\u001b[0m         \u001b[38;5;66;03m# get() on an attempt with an exception should cause it to be raised, but raise just in case\u001b[39;00m\n\u001b[1;32m--> 289\u001b[0m         \u001b[38;5;28;01mraise\u001b[39;00m attempt\u001b[38;5;241m.\u001b[39mget()\n\u001b[0;32m    290\u001b[0m     \u001b[38;5;28;01melse\u001b[39;00m:\n\u001b[0;32m    291\u001b[0m         \u001b[38;5;28;01mraise\u001b[39;00m RetryError(attempt)\n",
      "File \u001b[1;32m~\\anaconda3\\Lib\\site-packages\\retrying.py:326\u001b[0m, in \u001b[0;36mAttempt.get\u001b[1;34m(self, wrap_exception)\u001b[0m\n\u001b[0;32m    324\u001b[0m     \u001b[38;5;28;01melse\u001b[39;00m:\n\u001b[0;32m    325\u001b[0m         exc_type, exc, tb \u001b[38;5;241m=\u001b[39m \u001b[38;5;28mself\u001b[39m\u001b[38;5;241m.\u001b[39mvalue\n\u001b[1;32m--> 326\u001b[0m         \u001b[38;5;28;01mraise\u001b[39;00m exc\u001b[38;5;241m.\u001b[39mwith_traceback(tb)\n\u001b[0;32m    327\u001b[0m \u001b[38;5;28;01melse\u001b[39;00m:\n\u001b[0;32m    328\u001b[0m     \u001b[38;5;28;01mreturn\u001b[39;00m \u001b[38;5;28mself\u001b[39m\u001b[38;5;241m.\u001b[39mvalue\n",
      "File \u001b[1;32m~\\anaconda3\\Lib\\site-packages\\retrying.py:273\u001b[0m, in \u001b[0;36mRetrying.call\u001b[1;34m(self, fn, *args, **kwargs)\u001b[0m\n\u001b[0;32m    270\u001b[0m     \u001b[38;5;28mself\u001b[39m\u001b[38;5;241m.\u001b[39m_before_attempts(attempt_number)\n\u001b[0;32m    272\u001b[0m \u001b[38;5;28;01mtry\u001b[39;00m:\n\u001b[1;32m--> 273\u001b[0m     attempt \u001b[38;5;241m=\u001b[39m Attempt(fn(\u001b[38;5;241m*\u001b[39margs, \u001b[38;5;241m*\u001b[39m\u001b[38;5;241m*\u001b[39mkwargs), attempt_number, \u001b[38;5;28;01mFalse\u001b[39;00m)\n\u001b[0;32m    274\u001b[0m \u001b[38;5;28;01mexcept\u001b[39;00m \u001b[38;5;167;01mException\u001b[39;00m:\n\u001b[0;32m    275\u001b[0m     tb \u001b[38;5;241m=\u001b[39m sys\u001b[38;5;241m.\u001b[39mexc_info()\n",
      "File \u001b[1;32m~\\anaconda3\\Lib\\site-packages\\dash\\_jupyter.py:386\u001b[0m, in \u001b[0;36mJupyterDash.run_app.<locals>.wait_for_app\u001b[1;34m()\u001b[0m\n\u001b[0;32m    384\u001b[0m     \u001b[38;5;28;01mif\u001b[39;00m res \u001b[38;5;241m!=\u001b[39m \u001b[38;5;124m\"\u001b[39m\u001b[38;5;124mAlive\u001b[39m\u001b[38;5;124m\"\u001b[39m:\n\u001b[0;32m    385\u001b[0m         url \u001b[38;5;241m=\u001b[39m \u001b[38;5;124mf\u001b[39m\u001b[38;5;124m\"\u001b[39m\u001b[38;5;124mhttp://\u001b[39m\u001b[38;5;132;01m{\u001b[39;00mhost\u001b[38;5;132;01m}\u001b[39;00m\u001b[38;5;124m:\u001b[39m\u001b[38;5;132;01m{\u001b[39;00mport\u001b[38;5;132;01m}\u001b[39;00m\u001b[38;5;124m\"\u001b[39m\n\u001b[1;32m--> 386\u001b[0m         \u001b[38;5;28;01mraise\u001b[39;00m \u001b[38;5;167;01mOSError\u001b[39;00m(\n\u001b[0;32m    387\u001b[0m             \u001b[38;5;124mf\u001b[39m\u001b[38;5;124m\"\u001b[39m\u001b[38;5;124mAddress \u001b[39m\u001b[38;5;124m'\u001b[39m\u001b[38;5;132;01m{\u001b[39;00murl\u001b[38;5;132;01m}\u001b[39;00m\u001b[38;5;124m'\u001b[39m\u001b[38;5;124m already in use.\u001b[39m\u001b[38;5;130;01m\\n\u001b[39;00m\u001b[38;5;124m\"\u001b[39m\n\u001b[0;32m    388\u001b[0m             \u001b[38;5;124m\"\u001b[39m\u001b[38;5;124m    Try passing a different port to run.\u001b[39m\u001b[38;5;124m\"\u001b[39m\n\u001b[0;32m    389\u001b[0m         )\n\u001b[0;32m    390\u001b[0m \u001b[38;5;28;01mexcept\u001b[39;00m requests\u001b[38;5;241m.\u001b[39mConnectionError \u001b[38;5;28;01mas\u001b[39;00m err:\n\u001b[0;32m    391\u001b[0m     _get_error()\n",
      "\u001b[1;31mOSError\u001b[0m: Address 'http://127.0.0.1:8050' already in use.\n    Try passing a different port to run."
     ]
    }
   ],
   "source": [
    "# Run the app\n",
    "if __name__ == '__main__':\n",
    "    app.run(host='127.0.0.1', port=8050, debug=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "2fb3b3ac-3b2e-4052-a030-1def97e182d2",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.13.5"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
