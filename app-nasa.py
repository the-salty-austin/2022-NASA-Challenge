import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt

from lightkurve import search_targetpixelfile
import astropy.units as u

st.set_option('deprecation.showPyplotGlobalUse', False)

st.title('Light Curve Visualizer')

st.markdown("""
Analyze time series data on the brightness of planets, stars, and galaxies.
This app is focused on supporting science with NASA’s Kepler and TESS space telescopes.
* **Data source:** [Python Package - Lightkurve](https://docs.lightkurve.org/index.html).
""")

st.sidebar.header('Settings')

st.sidebar.subheader('1. Choose A Star!')
searchTarget = "KIC 6922244"
searchTarget = st.sidebar.text_area("Your Search", searchTarget, height=10)
st.sidebar.markdown("""
Searches can be based on a target’s coordinates, catalog ID number, or name:
* The name of the object as a string, for example, “Kepler-10.”
* The KIC or EPIC identifier as an integer, for example, “11904151.”
* A coordinate string in decimal format, for example, “285.67942179 +50.24130576.”
* A coordinate string in sexagesimal format, for example, “19:02:43.1 +50:14:28.7.”
""")

st.sidebar.header('2. Search Criteria')
selected_quarter = st.sidebar.slider('Quarter', 1, 17, 1 )

missions = ['Kepler', 'K2', 'TESS']
selected_mission = st.sidebar.multiselect('Mission', missions, missions)

authors = ['Kepler', 'K2', 'SPOC']
selected_author = st.sidebar.multiselect('Author', authors, authors)

st.header('1. Light Curve')
tpf = search_targetpixelfile(searchTarget, author=selected_author, mission=selected_mission, cadence="long", quarter=selected_quarter).download()
lc = tpf.to_lightcurve(aperture_mask=tpf.pipeline_mask)
lc.plot()
st.pyplot()

st.markdown('Long-term trend removed using [Savitzky–Golay filter](https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter).')
lc.remove_nans().flatten(window_length=401).plot()
st.pyplot()

fold = st.sidebar.slider('Fold', 0.01, 10.0, 3.5225 )
bin_size = st.sidebar.slider('Bin Size', 0.001, 10.0, 0.01 )
st.markdown(f'Long-term trend removed using [Savitzky–Golay filter](https://en.wikipedia.org/wiki/Savitzky%E2%80%93Golay_filter) / Phase folded by {fold} / Bin = {bin_size}')
lc.remove_nans().flatten(window_length=401).fold(period=fold).bin(time_bin_size=bin_size).plot()
st.pyplot()

st.header('2. Periodogram')
st.markdown("""
Periodograms of time series data can be useful for finding the periods of variable stars.
""")
pg = lc.to_periodogram(minimum_period=0.9*u.day, maximum_period=1.2*u.day, oversample_factor=10)
lc.fold(period=pg.period_at_max_power, wrap_phase=0.2).scatter()
st.pyplot()

st.header('3. Target Pixel Files')
maxFluxFrame = tpf.flux.shape[0]-1

st.sidebar.header('3. TargetPixelFile Frame')
frame = st.sidebar.slider('Frame Index', 1, maxFluxFrame, 1)

st.markdown(f"""
* TargetPixelFile (TPF) is a stack of images containing the flux in each pixel at each cadence.
* Current Frame UTC Time: {tpf.time.utc.iso[frame-1]} / Frame: {frame}
""")
tpf.plot(frame=frame)
st.pyplot()