import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Simulador Comercial - Final",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- CSS ADAPTATIVO (AUTO THEME) ---
st.markdown("""
<style>
    /* Cartões de Métricas */
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 15px;
        border-radius: 10px;
    }
    
    /* Caixa de Totalização */
    .total-box {
        padding: 20px; 
        border-radius: 10px; 
        text-align: center; 
        margin-top: 10px;
        background-color: rgba(39, 174, 96, 0.15);
        border: 2px solid #27ae60;
    }
    
    .total-title {
        color: inherit;
        font-size: 1.2rem;
        margin-bottom: 5px;
        opacity: 0.8;
    }
    
    .total-value {
        color: #27ae60;
        font-size: 3rem;
        font-weight: bold;
        margin: 0;
    }
    
    /* Tabelas limpas */
    .stDataFrame {
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES ---
def formatar_moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def calcular_comissao_closer(valor):
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

tab_closer, tab_sdr = st.tabs(["💼 Simulador CLOSER", "📡 Simulador SDR"])

# ==============================================================================
# ABA 1: CLOSER
# ==============================================================================
with tab_closer:
    col_input, col_resumo = st.columns([1, 2])

    # --- Lado Esquerdo: Inputs ---
    with col_input:
        st.subheader("Nova Loja")
        with st.form("form_loja"):
            valor_contrato = st.number_input("Valor do Contrato (R$)", min_value=0.0, step=1000.0)
            submitted = st.form_submit_button("➕ Adicionar ao Pipeline", use_container_width=True)
            
            if submitted and valor_contrato > 0:
                comissao, desc, icon = calcular_comissao_closer(valor_contrato)
                st.session_state['lojas'].append({
                    "Valor Contrato": valor_contrato,
                    "Classificação": f"{icon} {desc}",
                    "Comissão Prevista": comissao
                })
                st.toast(f"Loja adicionada!", icon="✅")

        if st.button("🗑️ Limpar Pipeline", use_container_width=True):
            st.session_state['lojas'] = []
            st.rerun()

        st.divider()
        
        # --- TABELA DE REFERÊNCIA (AGORA EM EXPANDER) ---
        with st.expander("📚 Ver Tabela de Comissões (Referência)"):
            st.caption("Valores baseados no fechamento individual.")
            
            df_referencia = pd.DataFrame({
                "Faixa de Contrato": [
                    "Abaixo de R$ 30k", 
                    "R$ 30k a R$ 39k", 
                    "R$ 40k a R$ 49k", 
                    "R$ 50k a R$ 59k", 
                    "R$ 60k a R$ 69k", 
                    "R$ 70k a R$ 89k", 
                    "Acima de R$ 90k"
                ],
                "Regra": [
                    "Zerado", 
                    "Base ÷ 2.0", 
                    "Base ÷ 1.5", 
                    "Base ÷ 1.2", 
                    "Base x 1.3", 
                    "Base x 1.5", 
                    "Base x 1.6"
                ],
                "Comissão (R$)": [
                    "R$ 0,00", 
                    "R$ 500,00", 
                    "R$ 666,67", 
                    "R$ 833,33", 
                    "R$ 1.300,00", 
                    "R$ 1.500,00", 
                    "R$ 1.600,00"
                ]
            })
            st.dataframe(df_referencia, hide_index=True, use_container_width=True)

    # --- Lado Direito: Resultados ---
    with col_resumo:
        total_fat = sum(l['Valor Contrato'] for l in st.session_state['lojas'])
        total_com_bruta = sum(l['Comissão Prevista'] for l in st.session_state['lojas'])
        gatilho_atingido = total_fat >= 100000
        comissao_final = total_com_bruta if gatilho_atingido else 0.00
        falta_gatilho = max(0, 100000 - total_fat)

        st.subheader("Painel de Performance")
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric("Pipeline Total", formatar_moeda(total_fat))
        kpi2.metric("Status Gatilho (100k)", "LIBERADO" if gatilho_atingido else "BLOQUEADO", 
                    delta=f"Superavit: {formatar_moeda(total_fat - 100000)}" if gatilho_atingido else f"- Falta {formatar_moeda(falta_gatilho)}",
                    delta_color="normal" if gatilho_atingido else "inverse")
        kpi3.metric("💰 Sua Comissão", formatar_moeda(comissao_final))

        progresso = min(total_fat / 100000, 1.0)
        st.progress(progresso, text=f"Progresso para desbloqueio: {int(progresso*100)}%")
        
        if st.session_state['lojas']:
            st.divider()
            df = pd.DataFrame(st.session_state['lojas'])
            df_disp = df.copy()
            df_disp['Valor Contrato'] = df_disp['Valor Contrato'].apply(formatar_moeda)
            df_disp['Comissão Prevista'] = df_disp['Comissão Prevista'].apply(formatar_moeda)
            st.dataframe(df_disp, use_container_width=True, hide_index=True)

# ==============================================================================
# ABA 2: SDR
# ==============================================================================
with tab_sdr:
    
    with st.expander("🕵️ Calculadora de Scorecard (Verificador)", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            s1 = 25 if st.checkbox("Unidades/Colab ≥ 200 (25 pts)") else 0
            s2 = 20 if st.checkbox("Urgência (20 pts)") else 0
            s3 = 20 if st.checkbox("Abertura (20 pts)") else 0
        with c2:
            s4 = 15 if st.checkbox("Dor clara (15 pts)") else 0
            s5 = 10 if st.checkbox("Histórico troca (10 pts)") else 0
            s6 = 10 if st.checkbox("Decisor acessível (10 pts)") else 0
        
        score = s1+s2+s3+s4+s5+s6
        st.write(f"**Score:** {score}/100")
        if score >= 75: st.success("✅ **HIGH SCORE!**")
        else: st.info("ℹ️ Lead Padrão")

    st.divider()
    st.subheader("💰 Simulador de Ganhos SDR")
    
    col_input, col_result = st.columns([1, 2])

    with col_input:
        st.markdown("**1. Produção**")
        leads_padrao = st.number_input("Qtd. Leads Qualificados (Padrão)", min_value=0, value=0)
        leads_high = st.number_input("Qtd. Leads High Score (Score ≥ 75)", min_value=0, value=0)
        
        st.markdown("**2. Conversão**")
        lojas = st.number_input("Lojas Fechadas (120d)", min_value=0, value=0)

    with col_result:
        # --- LÓGICA DE SOMA (PADRÃO + HIGH = META) ---
        total_leads_gerados = leads_padrao + leads_high
        meta_minima = 10
        meta_batida = total_leads_gerados >= meta_minima
        
        if meta_batida:
            val_padrao = leads_padrao * 20
            val_high = leads_high * 40
            status_meta = f"✅ Meta Batida ({total_leads_gerados} leads)"
            cor_meta = "normal"
        else:
            val_padrao = 0
            val_high = 0
            status_meta = f"❌ Meta não batida ({total_leads_gerados}/{meta_minima})"
            cor_meta = "inverse"
            
        val_lojas = lojas * 600
        total_sdr = val_padrao + val_high + val_lojas

        # --- EXIBIÇÃO ---
        c1, c2, c3 = st.columns(3)
        with c1: 
            st.metric("Pilar 1: Padrão", formatar_moeda(val_padrao), delta=status_meta, delta_color=cor_meta)
            st.caption(f"{leads_padrao} leads x R$ 20,00")
        with c2: 
            st.metric("Pilar 2: High Score", formatar_moeda(val_high), delta=status_meta, delta_color=cor_meta)
            st.caption(f"{leads_high} leads x R$ 40,00")
        with c3: 
            st.metric("Pilar 3: Lojas", formatar_moeda(val_lojas))
            st.caption(f"{lojas} lojas x R$ 600,00")

        st.markdown(f"""
        <div class="total-box">
            <div class="total-title">COMISSÃO TOTAL ESTIMADA</div>
            <div class="total-value">{formatar_moeda(total_sdr)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        if not meta_batida and total_leads_gerados > 0:
            st.warning(f"⚠️ Atenção: Você tem {total_leads_gerados} leads somados, mas precisa de no mínimo {meta_minima} (Padrão + High Score) para desbloquear.")