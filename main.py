import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Simulador Comercial",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SENHA DE ACESSO (Edite aqui) ---
SENHA_HEAD = "andersonamordaminhavida"  # <--- Defina a senha da Head aqui

# --- CSS ADAPTATIVO ---
st.markdown("""
<style>
    div[data-testid="stMetric"] {
        background-color: rgba(128, 128, 128, 0.1);
        border: 1px solid rgba(128, 128, 128, 0.2);
        padding: 15px;
        border-radius: 10px;
    }
    .total-box {
        padding: 20px; 
        border-radius: 10px; 
        text-align: center; 
        margin-top: 10px;
        background-color: rgba(39, 174, 96, 0.15);
        border: 2px solid #27ae60;
    }
    .total-value { color: #27ae60; font-size: 3rem; font-weight: bold; margin: 0; }
    
    .head-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-top: 10px;
        background: linear-gradient(45deg, rgba(52, 152, 219, 0.15), rgba(155, 89, 182, 0.15));
        border: 2px solid #3498db;
    }
    .head-value { color: #2980b9; font-size: 3.5rem; font-weight: bold; margin: 0; }
    
    /* Destaque na Tabela */
    .highlight-cell {
        background-color: #27ae60 !important;
        color: white !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNÇÕES ---
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

# --- ESTADO ---
if 'lojas' not in st.session_state:
    st.session_state['lojas'] = []

# --- TÍTULO ---
st.title("🎯 Central de Estratégia Comercial")
st.caption("Modelo: Matriz Progressiva de Liderança")

tab_closer, tab_sdr, tab_head = st.tabs(["💼 Simulador CLOSER", "📡 Simulador SDR", "🔒 Área da LIDERANÇA"])

# ==============================================================================
# ABA 1: CLOSER
# ==============================================================================
with tab_closer:
    col_input, col_resumo = st.columns([1, 2])
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

    with col_resumo:
        total_fat = sum(l['Valor Contrato'] for l in st.session_state['lojas'])
        total_com_bruta = sum(l['Comissão Prevista'] for l in st.session_state['lojas'])
        gatilho_atingido = total_fat >= 100000
        comissao_final_closer = total_com_bruta if gatilho_atingido else 0.00
        
        st.subheader("Performance do Closer")
        k1, k2, k3 = st.columns(3)
        k1.metric("Faturamento Total", formatar_moeda(total_fat))
        k2.metric("Gatilho 100k", "LIBERADO" if gatilho_atingido else "TRAVADO", 
                  delta="Bônus Ativo" if gatilho_atingido else "Sem Bônus")
        k3.metric("Comissão Closer", formatar_moeda(comissao_final_closer))
        
        if st.session_state['lojas']:
            st.divider()
            df = pd.DataFrame(st.session_state['lojas'])
            df['Valor Contrato'] = df['Valor Contrato'].apply(formatar_moeda)
            df['Comissão Prevista'] = df['Comissão Prevista'].apply(formatar_moeda)
            st.dataframe(df, use_container_width=True, hide_index=True)

# ==============================================================================
# ABA 2: SDR
# ==============================================================================
with tab_sdr:
    with st.expander("🕵️ Calculadora Scorecard"):
        st.caption("Ferramenta de validação rápida.")
        if st.checkbox("Unidades ≥ 200 (25pts)"): s=25 
        else: s=0

    st.divider()
    
    col_sdr_in, col_sdr_out = st.columns([1, 2])
    with col_sdr_in:
        st.markdown("**Produção**")
        l_padrao = st.number_input("Leads Padrão", 0)
        l_high = st.number_input("Leads High Score", 0)
        lojas = st.number_input("Lojas Fechadas", 0)
    with col_sdr_out:
        meta_min = 10
        total_leads = l_padrao + l_high
        batido = total_leads >= meta_min
        
        v_padrao = l_padrao * 20 if batido else 0
        v_high = l_high * 40
        v_lojas = lojas * 600
        total_sdr = v_padrao + v_high + v_lojas
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Padrão", formatar_moeda(v_padrao))
        c2.metric("High Score", formatar_moeda(v_high))
        c3.metric("Lojas", formatar_moeda(v_lojas))
        st.markdown(f"<div class='total-box'><div class='total-value'>{formatar_moeda(total_sdr)}</div></div>", unsafe_allow_html=True)

# ==============================================================================
# ABA 3: HEAD DE VENDAS (MATRIZ PROGRESSIVA)
# ==============================================================================
with tab_head:
    st.markdown("### 🔒 Painel da Liderança")
    
    input_senha = st.text_input("Senha de acesso:", type="password")
    
    if input_senha == SENHA_HEAD:
        st.success("Acesso Autorizado")
        
        # --- INPUTS DE CONTEXTO ---
        c_h_1, c_h_2 = st.columns(2)
        with c_h_1:
            st.markdown("##### 1. Dados do Closer")
            st.info(f"Comissão Atual do Closer: **{formatar_moeda(comissao_final_closer)}**")
            fat_total = sum(l['Valor Contrato'] for l in st.session_state['lojas'])
            
        with c_h_2:
            st.markdown("##### 2. Dados do SDR")
            meta_sdr_team = st.number_input("Meta High Score (Time)", value=20)
            realizado_sdr = st.number_input("High Score Entregues", min_value=0)
            pct_sdr = (realizado_sdr / meta_sdr_team) * 100 if meta_sdr_team > 0 else 0

        st.divider()

        # --- LÓGICA DA MATRIZ ---
        # Definindo Fator SDR (Linhas)
        if pct_sdr < 90:
            fator_sdr_idx = 0 # Ruim
            label_sdr = "Abaixo (<90%)"
        elif 90 <= pct_sdr < 100:
            fator_sdr_idx = 1 # Quase
            label_sdr = "Na Trave (90-99%)"
        else:
            fator_sdr_idx = 2 # Meta
            label_sdr = "Meta Batida (100%+)"

        # Definindo Fator Closer (Colunas)
        if fat_total < 100000:
            fator_closer_idx = -1 # Travado
            label_closer = "Abaixo de 100k"
        elif 100000 <= fat_total < 130000:
            fator_closer_idx = 0
            label_closer = "Base (100k-129k)"
        elif 130000 <= fat_total < 150000:
            fator_closer_idx = 1
            label_closer = "Tração (130k-149k)"
        else:
            fator_closer_idx = 2
            label_closer = "Excelência (150k+)"

        # --- MATRIZ DE MULTIPLICADORES ---
        # Linhas: SDR (Ruim, Médio, Bom)
        # Colunas: Closer (Base, Tração, Excelência)
        # Valores: Multiplicador sobre a comissão do Closer
        
        matriz = [
            [0.5, 0.6, 0.7],  # SDR Ruim (<90%)
            [0.8, 0.9, 1.0],  # SDR Médio (90-99%)
            [1.1, 1.2, 1.3]   # SDR Bom (100%+) -> AQUI ESTÁ O "POUCO A MAIS QUE O CLOSER"
        ]

        if fator_closer_idx == -1:
            multiplicador = 0.0
            msg_final = "❌ Closer não atingiu o gatilho mínimo de R$ 100k."
        else:
            multiplicador = matriz[fator_sdr_idx][fator_closer_idx]
            msg_final = f"✅ Fator Aplicado: **{multiplicador}x** sobre a comissão do Closer."

        comissao_head = comissao_final_closer * multiplicador

        # --- EXIBIÇÃO DA MATRIZ VISUAL ---
        st.subheader("📊 Tabela Progressiva (Seu Multiplicador)")
        
        # Criando DataFrame para exibição bonita
        df_matriz = pd.DataFrame(
            data=[
                ["0.5x (Penalidade)", "0.6x", "0.7x"],
                ["0.8x", "0.9x", "1.0x (Paridade)"],
                ["1.1x (Meta)", "1.2x", "1.3x (Super)"]
            ],
            columns=["Closer 100k+", "Closer 130k+", "Closer 150k+"],
            index=["SDR < 90%", "SDR 90-99%", "SDR 100%+"]
        )
        
        # Mostrando a tabela
        st.table(df_matriz)
        
        # Feedback do Cenário Atual
        if fator_closer_idx != -1:
            st.info(f"📍 **Situação Atual:** Closer na faixa **{label_closer}** e SDR na faixa **{label_sdr}**.")
        
        st.markdown(msg_final)

        # --- RESULTADO FINAL ---
        st.markdown(f"""
        <div class="head-box">
            <div class="total-title">COMISSÃO DA HEAD</div>
            <div class="head-value">{formatar_moeda(comissao_head)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Simulação de perda (FOMO)
        if multiplicador < 1.1 and comissao_final_closer > 0:
            potencial = comissao_final_closer * 1.1
            perda = potencial - comissao_head
            st.warning(f"💡 Se o time batesse a meta cheia (SDR 100% + Closer Base), você ganharia: **{formatar_moeda(potencial)}**. Dinheiro na mesa: {formatar_moeda(perda)}.")

    elif input_senha:
        st.error("Senha Incorreta")