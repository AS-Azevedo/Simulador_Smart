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
    .total-title { font-size: 1.2rem; opacity: 0.8; }
    .total-value { color: #27ae60; font-size: 3rem; font-weight: bold; margin: 0; }
    
    .head-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-top: 10px;
        background: linear-gradient(45deg, rgba(142, 68, 173, 0.15), rgba(41, 128, 185, 0.15));
        border: 2px solid #8e44ad;
    }
    .head-value { color: #9b59b6; font-size: 3.5rem; font-weight: bold; margin: 0; }
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
st.caption("1 Closer | 2 SDRs | 1 Head")

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

        with st.expander("📚 Tabela de Comissões"):
            st.markdown("""
            | Faixa | Regra | Valor |
            | :--- | :--- | :--- |
            | < 30k | Zerado | R$ 0 |
            | 30k-39k | ÷ 2.0 | R$ 500 |
            | 60k-69k | x 1.3 | R$ 1.300 |
            | ≥ 90k | x 1.6 | R$ 1.600 |
            """)

    with col_resumo:
        total_fat = sum(l['Valor Contrato'] for l in st.session_state['lojas'])
        total_com_bruta = sum(l['Comissão Prevista'] for l in st.session_state['lojas'])
        gatilho_atingido = total_fat >= 100000
        comissao_final = total_com_bruta if gatilho_atingido else 0.00
        
        st.subheader("Performance do Closer")
        k1, k2, k3 = st.columns(3)
        k1.metric("Faturamento Total", formatar_moeda(total_fat))
        k2.metric("Gatilho 100k", "LIBERADO" if gatilho_atingido else "TRAVADO", 
                  delta="Bônus Ativo" if gatilho_atingido else "Sem Bônus")
        k3.metric("Comissão Closer", formatar_moeda(comissao_final))
        
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
        if st.checkbox("Unidades ≥ 200 (25pts)"): s=25 
        else: s=0
        st.caption("Scorecard simplificado para verificação.")

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
        c1.metric("Padrão", formatar_moeda(v_padrao), delta="Meta Batida" if batido else "Abaixo Meta")
        c2.metric("High Score", formatar_moeda(v_high))
        c3.metric("Lojas", formatar_moeda(v_lojas))
        st.markdown(f"<div class='total-box'><div class='total-value'>{formatar_moeda(total_sdr)}</div></div>", unsafe_allow_html=True)

# ==============================================================================
# ABA 3: HEAD DE VENDAS (COM SENHA)
# ==============================================================================
with tab_head:
    st.markdown("### 🔒 Acesso Restrito à Liderança")
    
    # --- BLOQUEIO DE SEGURANÇA ---
    input_senha = st.text_input("Digite a senha de acesso:", type="password", help="Solicite ao administrador.")
    
    if input_senha == SENHA_HEAD:
        st.success("Acesso Liberado ✅")
        st.divider()
        
        # --- CONTEÚDO ORIGINAL DA HEAD (SÓ MOSTRA SE SENHA OK) ---
        col_h_input, col_h_res = st.columns([1, 2])

        with col_h_input:
            st.markdown("**1. Resultado Financeiro**")
            valor_auto = sum(l['Valor Contrato'] for l in st.session_state['lojas'])
            fat_closer = st.number_input("Faturamento (Closer)", min_value=0.0, value=float(valor_auto), step=1000.0)
            
            st.markdown("**2. Qualidade do Funil**")
            meta_sdr_team = st.number_input("Meta High Score (Time)", value=20)
            realizado_sdr = st.number_input("High Score Entregues", min_value=0)

        with col_h_res:
            # LÓGICA HEAD
            meta_sdr_batida = realizado_sdr >= meta_sdr_team
            
            if meta_sdr_batida:
                taxa_comissao = 0.05 
                desc_taxa = "🚀 5.0% (Qualidade OK)"
                cor_taxa = "normal"
            else:
                taxa_comissao = 0.025
                desc_taxa = "⚠️ 2.5% (Baixa Qualidade)"
                cor_taxa = "inverse"
                
            comissao_vendas = fat_closer * taxa_comissao
            
            bonus_fixo = 0.00
            desc_bonus = "❌ Sem Bônus"
            
            if fat_closer >= 150000:
                bonus_fixo = 4000.00
                desc_bonus = "🏆 R$ 4.000 (Excelência > 150k)"
            elif fat_closer >= 100000:
                bonus_fixo = 1500.00
                desc_bonus = "✅ R$ 1.500 (Meta > 100k)"
            
            total_head = comissao_vendas + bonus_fixo

            m1, m2, m3 = st.columns(3)
            m1.metric("Faturamento", formatar_moeda(fat_closer))
            m2.metric("Qualidade SDR", "Batida" if meta_sdr_batida else "Abaixo", delta=f"{int(realizado_sdr)}/{int(meta_sdr_team)}")
            m3.metric("Taxa Aplicada", f"{taxa_comissao*100:.1f}%", delta=desc_taxa, delta_color=cor_taxa)
            
            st.divider()
            
            c_venda, c_bonus = st.columns(2)
            c_venda.metric("Comissão Variável", formatar_moeda(comissao_vendas))
            c_bonus.metric("Bônus Performance", formatar_moeda(bonus_fixo), delta=desc_bonus)

            st.markdown(f"""
            <div class="head-box">
                <div class="total-title">COMISSÃO TOTAL (HEAD)</div>
                <div class="head-value">{formatar_moeda(total_head)}</div>
            </div>
            """, unsafe_allow_html=True)
            
    else:
        if input_senha:
            st.error("Senha incorreta. Acesso negado.")
        else:
            st.info("Digite a senha para visualizar o painel gerencial.")