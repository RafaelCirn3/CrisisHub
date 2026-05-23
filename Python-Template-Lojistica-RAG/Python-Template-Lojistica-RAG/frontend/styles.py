import streamlit as st


def apply_global_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg-main: #f6f8fb;
            --bg-soft: #ffffff;
            --txt-main: #111827;
            --txt-soft: #4b5563;
            --brand: #b91c1c;
            --brand-soft: #fee2e2;
            --ok: #166534;
            --border: #e5e7eb;
        }

        .stApp {
            background:
                radial-gradient(circle at 10% 10%, #ffe4e6 0%, transparent 22%),
                radial-gradient(circle at 90% 20%, #fef3c7 0%, transparent 25%),
                var(--bg-main);
            color: var(--txt-main);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #111827 0%, #1f2937 100%);
        }

        [data-testid="stSidebar"] * {
            color: #f9fafb;
        }

        .hero {
            background: linear-gradient(135deg, #ffffff 0%, #fff1f2 100%);
            border: 1px solid var(--border);
            border-left: 6px solid var(--brand);
            border-radius: 14px;
            padding: 1rem 1.2rem;
            margin-bottom: 1rem;
        }

        .card {
            background: var(--bg-soft);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 0.9rem 1rem;
            margin-bottom: 0.8rem;
        }

        .step-chip {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 700;
            background: var(--brand-soft);
            color: #7f1d1d;
            border: 1px solid #fecaca;
            margin-bottom: .5rem;
        }

        .muted {
            color: var(--txt-soft);
            font-size: .92rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
