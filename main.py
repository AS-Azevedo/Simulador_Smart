import streamlit as st
import pandas as pd

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Simulador Comercial - Versão Final",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SENHA DE ACESSO HEAD ---
SENHA_HEAD = "andersonamordaminhavida"

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
    .total-value { color: #27ae60; font-size: 3rem; font-weight: bold; margin: 0; }
    
    /* Caixa da Head */
    .head-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-top: 10px;
        background: linear-gradient(45deg, rgba(41, 128, 185, 0.15), rgba(142, 68, 173, 0.15));
        border: 2px solid #2980b9;
    }
    .head-value { color: #2980b9; font-size: 3.5rem; font-weight: bold; margin: 0; }
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
st.caption("Sistema Unificado: Closer | SDR | Head")

tab_closer, tab_sdr, tab_head = st.tabs(["💼 Simulador CLOSER", "📡 Simulador SDR", "🔒 Área da LIDERANÇA"])

# ==============================================================================
# ABA 1: CLOSER
# ==============================================================================
with tab_closer:
    col_input, col_resumo = st.columns([1, 2])
    
    # --- Coluna Esquerda: Inputs + TABELA RESTAURADA ---
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
        
        # --- TABELA DE COMISSÃO (RESTAURADA) ---
        with st.expander("📚 Ver Tabela de Comissões (Referência)", expanded=False):
            st.caption("Regra de pagamento por loja individual:")
            df_ref = pd.DataFrame({
                "Faturamento": ["< 30k", "30k - 39k", "40k - 49k", "50k - 59k", "60k - 69k", "70k - 89k", "≥ 90k"],
                "Fator": ["Zerado", "Base ÷ 2.0", "Base ÷ 1.5", "Base ÷ 1.2", "Base x 1.3", "Base x 1.5", "Base x 1.6"],
                "Comissão": ["R$ 0", "R$ 500", "R$ 666", "R$ 833", "R$ 1.300", "R$ 1.500", "R$ 1.600"]
            })
            st.dataframe(df_ref, hide_index=True, use_container_width=True)

    # --- Coluna Direita: Resultados ---
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
    
    # --- CALCULADORA DE SCORECARD (RESTAURADA) ---
    with st.expander("🕵️ Calculadora: Esse lead é High Score?", expanded=False):
        st.caption("Marque os itens presentes no lead. Soma necessária: 75 pontos.")
        c1, c2 = st.columns(2)
        with c1:
            s1 = 25 if st.checkbox("Unidades/Colab ≥ 200 (25 pts)") else 0
            s2 = 20 if st.checkbox("Urgência do projeto (20 pts)") else 0
            s3 = 20 if st.checkbox("Abertura para proposta (20 pts)") else 0
        with c2:
            s4 = 15 if st.checkbox("Dor clara identificada (15 pts)") else 0
            s5 = 10 if st.checkbox("Histórico troca fornecedor (10 pts)") else 0
            s6 = 10 if st.checkbox("Decisor acessível (10 pts)") else 0
        
        score_atual = s1+s2+s3+s4+s5+s6
        st.markdown(f"**Score Total:** `{score_atual} / 100`")
        
        if score_atual >= 75:
            st.success("✅ **HIGH SCORE!** Pode cadastrar como Lead High Score.")
        else:
            st.warning("ℹ️ **LEAD PADRÃO.** Cadastre como Lead Qualificado Normal.")

    st.divider()
    
    col_sdr_in, col_sdr_out = st.columns([1, 2])
    with col_sdr_in:
        st.markdown("**Produção Mensal**")
        l_padrao = st.number_input("Qtd. Leads Padrão (< 75 pts)", 0)
        l_high = st.number_input("Qtd. Leads High Score (≥ 75 pts)", 0)
        lojas = st.number_input("Lojas Fechadas (120 dias)", 0)
        
    with col_sdr_out:
        meta_min = 10
        total_leads = l_padrao + l_high
        batido = total_leads >= meta_min
        
        v_padrao = l_padrao * 20 if batido else 0
        v_high = l_high * 40
        v_lojas = lojas * 600
        total_sdr = v_padrao + v_high + v_lojas
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Padrão", formatar_moeda(v_padrao), delta="Meta Batida" if batido else "Abaixo Meta")
        c2.metric("High Score", formatar_moeda(v_high))
        c3.metric("Lojas", formatar_moeda(v_lojas))
        st.markdown(f"<div class='total-box'><div class='total-value'>{formatar_moeda(total_sdr)}</div></div>", unsafe_allow_html=True)

# ==============================================================================
# ABA 3: HEAD DE VENDAS (MATRIZ CONSERVADORA)
# ==============================================================================
with tab_head:
    st.markdown("### 🔒 Painel da Liderança")
    
    input_senha = st.text_input("Senha de acesso:", type="password")
    
    if input_senha == SENHA_HEAD:
        st.success("Acesso Autorizado")
        
        # --- INPUTS ---
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

        # --- LÓGICA DA MATRIZ CONSERVADORA (+5% a +15%) ---
        
        # 1. Definindo Linha (SDR)
        if pct_sdr < 90:
            fator_sdr_idx = 0 # Ruim
            label_sdr = "Abaixo (<90%)"
        elif 90 <= pct_sdr < 100:
            fator_sdr_idx = 1 # Médio
            label_sdr = "Quase (90-99%)"
        else:
            fator_sdr_idx = 2 # Bom
            label_sdr = "Meta Batida (100%+)"

        # 2. Definindo Coluna (Closer)
        if fat_total < 100000:
            fator_closer_idx = -1
            label_closer = "Sem Comissão (<100k)"
        elif 100000 <= fat_total < 130000:
            fator_closer_idx = 0
            label_closer = "Base (100k+)"
        elif 130000 <= fat_total < 150000:
            fator_closer_idx = 1
            label_closer = "Tração (130k+)"
        else:
            fator_closer_idx = 2
            label_closer = "Excelência (150k+)"

        # --- A MATRIZ "APENAS UM POUCO MAIOR" ---
        matriz = [
            [0.80, 0.85, 0.90],  # SDR Ruim (Head ganha MENOS que Closer)
            [0.95, 1.00, 1.00],  # SDR Médio (Head empata com Closer)
            [1.05, 1.10, 1.15]   # SDR Bom (Head ganha de 5% a 15% a mais)
        ]

        if fator_closer_idx == -1:
            multiplicador = 0.0
            msg_final = "❌ Closer não atingiu o gatilho mínimo. Sem comissão para Head."
        else:
            multiplicador = matriz[fator_sdr_idx][fator_closer_idx]
            msg_final = f"✅ Fator Aplicado: **{multiplicador}x** sobre o ganho do Closer."

        comissao_head = comissao_final_closer * multiplicador

        # --- VISUALIZAÇÃO ---
        st.subheader("📊 Matriz de Multiplicadores")
        st.caption("Quanto você ganha em relação ao Closer (Ex: 1.10x = Ganho do Closer + 10%)")
        
        df_matriz = pd.DataFrame(
            data=[
                ["0.80x (-20%)", "0.85x", "0.90x (-10%)"],
                ["0.95x", "1.00x (Igual)", "1.00x (Igual)"],
                ["1.05x (+5%)", "1.10x (+10%)", "1.15x (+15%)"]
            ],
            columns=["Closer 100k", "Closer 130k", "Closer 150k"],
            index=["SDR < 90%", "SDR 90-99%", "SDR 100%+"]
        )
        # Use st.table para forçar visualização completa
        st.table(df_matriz)
        
        if fator_closer_idx != -1:
            # Destaque do cenário atual
            st.info(f"📍 **Seu Cenário:** Closer **{label_closer}** & SDR **{label_sdr}**")
        
        st.markdown(msg_final)

        st.markdown(f"""
        <div class="head-box">
            <div class="total-title">COMISSÃO DA HEAD</div>
            <div class="head-value">{formatar_moeda(comissao_head)}</div>
        </div>
        """, unsafe_allow_html=True)

    elif input_senha:
        st.error("Senha Incorreta")