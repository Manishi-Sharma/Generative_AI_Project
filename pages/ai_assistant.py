"""
Page: AI Financial Assistant (NVIDIA NIM Nemotron Integration)
Interactive organisation-aware conversational decision support,
quick strategic queries, and audited interaction logs.
"""

from typing import Any
import streamlit as st
from database.connection import get_db_context
from modules.ai_assistant import ask_financial_assistant, get_ai_history
from modules.nvidia_client import nvidia_client


def render_ai_assistant_page(current_user: Any, current_org: Any) -> None:
    st.markdown("## 🤖 NVIDIA Nemotron AI Financial Copilot")
    st.markdown(f"**Entity:** `{current_org.name}` | Authorised Decision-Support Assistant")

    is_online, status_msg = nvidia_client.is_available()
    if is_online:
        st.success(f"🟢 **NVIDIA NIM Online:** {status_msg}")
    else:
        st.info(f"⚡ **Autonomous Fallback Active:** {status_msg}")

    tab_chat, tab_history = st.tabs(["💬 Interactive Copilot", "📜 Audited Query History"])

    with tab_chat:
        st.markdown("#### Quick Strategic Financial Queries")
        quick_questions = [
            "What happens if we reduce expenses by 5%?",
            "How can we improve cash reserves without damaging growth?",
            "Which department has the greatest savings opportunity?",
            "Explain our financial ripple effects and second-order traps.",
            "What are the risks of increasing investment capital?",
            "Explain our current balance sheet and financial position.",
        ]

        q_cols = st.columns(3)
        selected_prompt = None
        for i, q in enumerate(quick_questions):
            with q_cols[i % 3]:
                if st.button(f"💡 {q}", key=f"quick_btn_{i}", use_container_width=True):
                    selected_prompt = q

        # Chat history state
        if "chat_messages" not in st.session_state:
            st.session_state["chat_messages"] = [
                {
                    "role": "assistant",
                    "content": (
                        f"Greetings. I am your strategic AI financial copilot for **{current_org.name}**. "
                        "I analyze your live ledger balances, multi-order ripple dependencies, and stress scenarios. "
                        "How may I advise your executive team today?"
                    ),
                    "model": "Nemotron",
                }
            ]

        # Display history
        for msg in st.session_state["chat_messages"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if "model" in msg and msg["role"] == "assistant":
                    st.caption(f"🧠 Model: `{msg['model']}`")

        # Handle user input via chat input or quick button
        user_query = st.chat_input("Enter your financial inquiry...")
        prompt_to_send = selected_prompt or user_query

        if prompt_to_send:
            # Append user message
            st.session_state["chat_messages"].append({"role": "user", "content": prompt_to_send})
            with st.chat_message("user"):
                st.markdown(prompt_to_send)

            with st.chat_message("assistant"):
                with st.spinner("Analyzing financial models and synthesizing ripple effects..."):
                    with get_db_context() as db:
                        res = ask_financial_assistant(
                            db=db,
                            org_id=current_org.id,
                            user_id=current_user.id,
                            user_query=prompt_to_send,
                        )
                    st.markdown(res["response"])
                    st.caption(f"🧠 Model: `{res['model']}` {'(Offline Expert Fallback)' if res['was_fallback'] else '(NVIDIA NIM)'}")

            st.session_state["chat_messages"].append({
                "role": "assistant",
                "content": res["response"],
                "model": res["model"],
            })

    with tab_history:
        st.markdown("### Audited AI Inquiries & Strategic History")
        with get_db_context() as db:
            history = get_ai_history(db, current_org.id, limit=15)

        if not history:
            st.info("No prior AI inquiries recorded for this organisation.")
        else:
            for item in history:
                with st.expander(f"🕒 {item.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')} — {item.prompt[:70]}..."):
                    st.markdown(f"**Query:** {item.prompt}")
                    st.markdown(f"**Engine Used:** `{item.model_used}` {'(Fallback)' if item.was_fallback else '(NVIDIA NIM)'}")
                    st.markdown("---")
                    st.markdown(item.response)
