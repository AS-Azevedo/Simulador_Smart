import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Simulador de Comissionamento",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILIZAÇÃO CSS (Visual Clean) ---
st.markdown("""
<style>
    .stMetric {
        background-color: #f9f9f9;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    .stButton button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        font-weight: bold;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
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

# --- INICIALIZAÇÃO DE ESTADO (MEMÓRIA) ---
if 'lojas' not in st.session_state:
    st.session_state['lojas'] = []

# --- CABEÇALHO ---
st.title("🎯 Central de Estratégia Comercial")
st.markdown("Simulador oficial de remuneração variável e análise de ICP.")

# --- ABAS DE NAVEGAÇÃO ---
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
        # Cálculos Totais
        total_fat = sum(l['Valor Contrato'] for l in st.session_state['lojas'])
        total_com_bruta = sum(l['Comissão Prevista'] for l in st.session_state['lojas'])
        gatilho_atingido = total_fat >= 100000
        comissao_final = total_com_bruta if gatilho_atingido else 0.00
        falta_gatilho = max(0, 100000 - total_fat)

        # Painel de Métricas (KPIs)
        st.subheader("Painel de Performance")
        kpi1, kpi2, kpi3 = st.columns(3)
        
        kpi1.metric("Pipeline Total", formatar_moeda(total_fat))
        
        kpi2.metric(
            "Status Gatilho (100k)", 
            "LIBERADO" if gatilho_atingido else "BLOQUEADO",
            delta=f"Superou em {formatar_moeda(total_fat - 100000)}" if gatilho_atingido else f"- Falta {formatar_moeda(falta_gatilho)}",
            delta_color="normal" if gatilho_atingido else "inverse"
        )
        
        kpi3.metric(
            "💰 Sua Comissão", 
            formatar_moeda(comissao_final),
            delta="Confirmado" if gatilho_atingido else "Pendente",
            delta_color="normal" if gatilho_atingido else "off"
        )

        # Barra de Progresso Visual
        progresso = min(total_fat / 100000, 1.0)
        st.progress(progresso, text=f"Progresso para desbloqueio: {int(progresso*100)}%")
        
        if not gatilho_atingido and total_fat > 0:
            st.warning("⚠️ Você precisa atingir R$ 100.000,00 para desbloquear o pagamento.")
        elif gatilho_atingido:
            st.success("✅ Gatilho atingido! Comissão liberada.")

        # Tabela Detalhada
        if st.session_state['lojas']:
            st.divider()
            st.caption("Extrato Detalhado por Loja")
            df = pd.DataFrame(st.session_state['lojas'])
            
            # Formatação para exibição
            df_display = df.copy()
            df_display['Valor Contrato'] = df_display['Valor Contrato'].apply(formatar_moeda)
            df_display['Comissão Prevista'] = df_display['Comissão Prevista'].apply(formatar_moeda)
            
            st.dataframe(df_display, use_container_width=True, hide_index=True)

# ==============================================================================
# ABA SDR
# ==============================================================================
with tab_sdr:
    st.info("💡 **Regra:** Volume sem qualidade paga zero. Qualidade sem fechamento paga pouco. O foco é LOJA.")
    
    col_sdr_input, col_sdr_result = st.columns([1, 2])

    with col_sdr_input:
        st.subheader("Entrada de Produção")
        
        leads_qualificados = st.number_input("1️⃣ Leads Qualificados (SQLs)", min_value=0, value=0, help="Empresas/Condomínios com decisor e contexto.")
        leads_high_score = st.number_input("2️⃣ Desses, quantos High Score?", min_value=0, value=0, help="Pontuação ≥ 75 no Scorecard.")
        lojas_fechadas = st.number_input("3️⃣ Lojas Fechadas (Ciclo 120d)", min_value=0, value=0, help="Contratos assinados originados pelo SDR.")

        # Validação Lógica
        if leads_high_score > leads_qualificados:
            st.warning("Atenção: High Score não pode ser maior que o Total de Leads.")
            leads_high_score = leads_qualificados

    with col_sdr_result:
        # Cálculos SDR
        # Pilar 1
        p1_val = leads_qualificados * 20 if leads_qualificados >= 10 else 0
        p1_status = "✅ Meta Batida" if leads_qualificados >= 10 else "❌ Meta não atingida (<10)"
        
        # Pilar 2
        p2_val = leads_high_score * 40
        
        # Pilar 3
        p3_val = lojas_fechadas * 600
        
        total_sdr = p1_val + p2_val + p3_val

        st.subheader("Extrato de Remuneração")

        c1, c2, c3 = st.columns(3)
        
        with c1:
            st.metric("Pilar 1: Volume", formatar_moeda(p1_val), delta=p1_status)
            st.caption("R$ 20/lead (Se > 10)")
        
        with c2:
            st.metric("Pilar 2: Qualidade", formatar_moeda(p2_val))
            st.caption(f"{leads_high_score} High Score x R$ 40")
            
        with c3:
            st.metric("Pilar 3: Receita", formatar_moeda(p3_val))
            st.caption(f"{lojas_fechadas} Lojas x R$ 600")

        st.divider()
        
        # Totalzão
        st.markdown(f"""
        <div style="text-align: center; background-color: #d4edda; padding: 20px; border-radius: 10px; border: 1px solid #c3e6cb;">
            <h3 style="color: #155724; margin:0;">COMISSÃO TOTAL ESTIMADA</h3>
            <h1 style="color: #155724; margin:0; font-size: 3em;">{formatar_moeda(total_sdr)}</h1>
        </div>
        """, unsafe_allow_html=True)