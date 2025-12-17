import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Simulador Comercial - Dark Mode",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILIZAÇÃO CSS (MODO ESCURO / DARK MODE) ---
st.markdown("""
<style>
    /* Fundo Geral */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Cartões de Métricas */
    div[data-testid="stMetric"], .stMetric {
        background-color: #262730 !important;
        border: 1px solid #303030;
        padding: 15px;
        border-radius: 10px;
        color: white !important;
    }
    
    /* Textos de Label de Métrica */
    div[data-testid="stMetricLabel"] {
        color: #A0A0A0 !important;
    }
    
    /* Valor da Métrica */
    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }

    /* Inputs numéricos */
    .stNumberInput input {
        background-color: #1A1C24;
        color: white;
    }

    /* Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1A1C24;
        border-radius: 4px;
        color: #FAFAFA;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FF4B4B !important;
        color: white !important;
    }

    /* Tabelas */
    .stDataFrame, .stTable {
        background-color: #262730; 
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_comissao_individual(valor):
    base = 1000.00
    if valor < 30000: return 0.00, "Abaixo do Piso", "🔴"
    elif 30000 <= valor < 40000: return base / 2.0, "Ticket Mínimo", "🟠"
    elif 40000 <= valor < 50000: return base / 1.5, "Médio-Baixo", "🟡"
    elif 50000 <= valor < 60000: return base / 1.2, "Médio", "🟡"
    elif 60000 <= valor < 70000: return base * 1.3, "Bom Ticket", "🟢"
    elif 70000 <= valor < 90000: return base * 1.5, "Ticket Alto", "🟢"
    else: return base * 1.6, "ICP Ouro (Excelente)", "🌟"

# --- INICIALIZAÇÃO DE ESTADO ---
if 'lojas' not in st.session_state:
    st.session_state['lojas'] = []

# --- TÍTULO ---
st.title("🎯 Central de Estratégia Comercial")

# --- ABAS ---
tab_closer, tab_sdr = st.tabs(["💼 Simulador CLOSER", "📡 Simulador SDR"])

# ==============================================================================
# ABA CLOSER
# ==============================================================================
with tab_closer:
    col_input, col_resumo = st.columns([1, 2])

    with col_input:
        st.subheader("Nova Loja")
        with st.form("form_loja"):
            valor_contrato = st.number_input("Valor do Contrato (R$)", min_value=0.0, step=1000.0)
            submitted = st.form_submit_button("➕ Adicionar ao Pipeline")
            
            if submitted and valor_contrato > 0:
                comissao, desc, icon = calcular_comissao_individual(valor_contrato)
                st.session_state['lojas'].append({
                    "Valor Contrato": valor_contrato,
                    "Classificação": f"{icon} {desc}",
                    "Comissão Prevista": comissao
                })
                st.toast(f"Loja de {formatar_moeda(valor_contrato)} adicionada!", icon="✅")

        if st.button("🗑️ Limpar Pipeline"):
            st.session_state['lojas'] = []
            st.rerun()

    with col_resumo:
        total_fat = sum(l['Valor Contrato'] for l in st.session_state['lojas'])
        total_com_bruta = sum(l['Comissão Prevista'] for l in st.session_state['lojas'])
        gatilho_atingido = total_fat >= 100000
        comissao_final = total_com_bruta if gatilho_atingido else 0.00
        falta_gatilho = max(0, 100000 - total_fat)

        st.subheader("Painel de Performance")
        kpi1, kpi2, kpi3 = st.columns(3)
        
        kpi1.metric("Pipeline Total", formatar_moeda(total_fat))
        
        kpi2.metric(
            "Status Gatilho (100k)", 
            "LIBERADO" if gatilho_atingido else "BLOQUEADO",
            delta=f"+ {formatar_moeda(total_fat - 100000)}" if gatilho_atingido else f"- Falta {formatar_moeda(falta_gatilho)}",
            delta_color="normal" if gatilho_atingido else "inverse"
        )
        
        kpi3.metric(
            "💰 Sua Comissão", 
            formatar_moeda(comissao_final),
            delta="Confirmado" if gatilho_atingido else "Pendente",
        )

        progresso = min(total_fat / 100000, 1.0)
        st.progress(progresso, text=f"Progresso para desbloqueio: {int(progresso*100)}%")
        
        if st.session_state['lojas']:
            st.divider()
            df = pd.DataFrame(st.session_state['lojas'])
            df_display = df.copy()
            df_display['Valor Contrato'] = df_display['Valor Contrato'].apply(formatar_moeda)
            df_display['Comissão Prevista'] = df_display['Comissão Prevista'].apply(formatar_moeda)
            st.dataframe(df_display, use_container_width=True, hide_index=True)

# ==============================================================================
# ABA SDR (ATUALIZADA)
# ==============================================================================
with tab_sdr:
    
    # --- CALCULADORA DE SCORECARD (NOVIDADE) ---
    with st.expander("🕵️ Calculadora Rápida: Esse Lead é High Score?", expanded=True):
        st.markdown("Marque o que o lead possui:")
        col_checks_1, col_checks_2 = st.columns(2)
        
        with col_checks_1:
            c1 = st.checkbox("Nº Unidades/Colaboradores ≥ 200 (25 pts)")
            c2 = st.checkbox("Urgência do projeto (20 pts)")
            c3 = st.checkbox("Abertura para proposta (20 pts)")
        
        with col_checks_2:
            c4 = st.checkbox("Dor clara identificada (15 pts)")
            c5 = st.checkbox("Histórico troca fornecedor (10 pts)")
            c6 = st.checkbox("Tipo de síndico/decisor acessível (10 pts)")
        
        score_atual = (25 if c1 else 0) + (20 if c2 else 0) + (20 if c3 else 0) + \
                      (15 if c4 else 0) + (10 if c5 else 0) + (10 if c6 else 0)
        
        st.write(f"**Score Atual:** {score_atual} / 100")
        
        if score_atual >= 75:
            st.success("✅ **É UM LEAD HIGH SCORE!** (Contebilize abaixo)")
        else:
            st.error(f"❌ Lead Comum (Faltam {75 - score_atual} pontos para High Score)")

    st.divider()

    # --- DEFINIÇÃO DO QUE É HIGH SCORE (TABELA FIXA) ---
    st.subheader("📚 Critérios de Qualidade (Scorecard Oficial)")
    df_rules = pd.DataFrame({
        "Critério": [
            "Nº de unidades / colaboradores",
            "Urgência do projeto",
            "Abertura para proposta",
            "Dor clara identificada",
            "Histórico de troca de fornecedor",
            "Tipo de síndico"
        ],
        "Peso (Pontos)": [25, 20, 20, 15, 10, 10],
        "Importância": ["Alto 🔴", "Alto 🔴", "Alto 🔴", "Médio 🟡", "Médio 🟡", "Baixo 🔵"]
    })
    st.table(df_rules)
    st.caption("ℹ️ **High Score:** Leads que somam **75 pontos ou mais**.")

    st.divider()

    # --- SIMULADOR FINANCEIRO ---
    st.subheader("💰 Simulador de Ganhos SDR")
    
    col_sdr_input, col_sdr_result = st.columns([1, 2])

    with col_sdr_input:
        leads_qualificados = st.number_input("1️⃣ Total Leads Qualificados (SQLs)", min_value=0, value=0)
        leads_high_score = st.number_input("2️⃣ Desses, quantos High Score?", min_value=0, value=0)
        lojas_fechadas = st.number_input("3️⃣ Lojas Fechadas (Ciclo 120d)", min_value=0, value=0)

        if leads_high_score > leads_qualificados:
            st.warning("High Score ajustado para igualar o total.")
            leads_high_score = leads_qualificados

    with col_sdr_result:
        # Cálculos
        p1_val = leads_qualificados * 20 if leads_qualificados >= 10 else 0
        p2_val = leads_high_score * 40
        p3_val = lojas_fechadas * 600
        total_sdr = p1_val + p2_val + p3_val

        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Pilar 1: Volume", formatar_moeda(p1_val))
        with c2: st.metric("Pilar 2: Qualidade", formatar_moeda(p2_val))
        with c3: st.metric("Pilar 3: Receita", formatar_moeda(p3_val))

        st.markdown(f"""
        <div style="text-align: center; background-color: #262730; padding: 20px; border-radius: 10px; border: 1px solid #444; margin-top: 10px;">
            <h3 style="color: #A0A0A0; margin:0; font-size: 1rem;">COMISSÃO TOTAL ESTIMADA</h3>
            <h1 style="color: #00FF7F; margin:0; font-size: 3em;">{formatar_moeda(total_sdr)}</h1>
        </div>
        """, unsafe_allow_html=True)