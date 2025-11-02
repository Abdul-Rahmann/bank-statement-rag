"""
Chat Page
Interactive chat interface with the AI assistant
"""

import streamlit as st
from streamlit_app.charts import generate_chart_for_query


def render():
    """Render the chat page."""
    st.markdown('<p class="main-header">Chat Assistant</p>', unsafe_allow_html=True)

    if st.session_state.rag is None:
        st.warning("Please initialize the system first.")
        return

    # Chat history
    chat_container = st.container()

    with chat_container:
        for idx, message in enumerate(st.session_state.chat_history):
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "chart" in message:
                    st.plotly_chart(message["chart"], use_container_width=True, key=f"chat_chart_{idx}")

    # Chat input
    if prompt := st.chat_input("Ask about your transactions..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.rag.ask(prompt)
                st.markdown(response)

                chart = generate_chart_for_query(prompt, st.session_state.transactions_df)
                if chart:
                    chart_idx = len(st.session_state.chat_history)
                    st.plotly_chart(chart, use_container_width=True, key=f"chat_chart_{chart_idx}")
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response,
                        "chart": chart
                    })
                else:
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": response
                    })