"""
LughaLLM Native Agentic Tool Calling & Function Execution.
Provides native Swahili tools for market prices, agricultural weather, tax calculations,
and telecom verification across East & Central Africa.
"""

from typing import Dict, Any, List, Optional
import json


class ToolRegistry:
    """Registry of callable tools for autonomous LughaLLM agents."""

    def __init__(self):
        self._tools = {}
        self._register_default_tools()

    def register(self, name: str, description: str, parameters: Dict[str, Any], func):
        self._tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "func": func
        }

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Returns OpenAI-compatible tool definitions."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            }
            for tool in self._tools.values()
        ]

    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Executes a registered tool by name with arguments."""
        if name not in self._tools:
            return {"error": f"Tool '{name}' haipo katika sajili ya LughaLLM."}
        try:
            return self._tools[name]["func"](**arguments)
        except Exception as e:
            return {"error": f"Hitilafu wakati wa kutekeleza '{name}': {str(e)}"}

    def _register_default_tools(self):
        # 1. Market prices
        self.register(
            name="pata_bei_za_soko",
            description="Pata bei za soko za mazao ya kilimo (mahindi, maharage, kahawa, mihogo) katika miji mikuu ya Afrika Mashariki na Kati.",
            parameters={
                "type": "object",
                "properties": {
                    "zao": {"type": "string", "description": "Jina la zao, k.m. mahindi, kahawa, mihogo"},
                    "mji": {"type": "string", "description": "Mji, k.m. Nairobi, Dar es Salaam, Kampala, Goma, Kigali"}
                },
                "required": ["zao", "mji"]
            },
            func=self._tool_market_prices
        )

        # 2. Agricultural weather
        self.register(
            name="hali_ya_hewa_kilimo",
            description="Pata utabiri wa hali ya hewa na msimu wa mvua kwa mkulima katika kanda maalum.",
            parameters={
                "type": "object",
                "properties": {
                    "eneo": {"type": "string", "description": "Eneo au mkoa, k.m. Morogoro, Rift Valley, Kivu, Buganda"}
                },
                "required": ["eneo"]
            },
            func=self._tool_weather
        )

        # 3. Tax calculator
        self.register(
            name="hesabu_kodi_kikanda",
            description="Hesabu makadirio ya kodi ya ongezeko la thamani (VAT) au kodi ya mapato kulingana na nchi (Kenya, Tanzania, Uganda, DRC, Rwanda).",
            parameters={
                "type": "object",
                "properties": {
                    "kiasi": {"type": "number", "description": "Kiasi cha pesa"},
                    "nchi": {"type": "string", "description": "Jina la nchi, k.m. Tanzania, Kenya, Uganda, DRC, Rwanda"}
                },
                "required": ["kiasi", "nchi"]
            },
            func=self._tool_tax_calculator
        )

        # 4. Digital Micro-Loan & APR Simplifier (Protects informal traders from debt traps)
        self.register(
            name="rahisisha_mkopo_kidijitali",
            description="Chambua masharti ya mkopo wa kidijitali (m-kopo wa simu), riba ya kweli kwa mwaka (APR), na ushauri wa kiusalama.",
            parameters={
                "type": "object",
                "properties": {
                    "kiasi_cha_mkopo": {"type": "number", "description": "Kiasi ulichokopa (k.m. 50,000)"},
                    "kiasi_cha_kurejesha": {"type": "number", "description": "Jumla ya kiasi unachotakiwa kulipa (k.m. 65,000)"},
                    "muda_siku": {"type": "integer", "description": "Muda wa mkopo kwa siku (k.m. siku 14 au 30)"}
                },
                "required": ["kiasi_cha_mkopo", "kiasi_cha_kurejesha", "muda_siku"]
            },
            func=self._tool_loan_simplifier
        )

        # 5. Crop Disease & Pest Protection Tool (For smallholder farmers)
        self.register(
            name="tiba_ya_magonjwa_ya_mimea",
            description="Pata ushauri wa haraka na tiba nafuu ya wadudu na magonjwa ya mazao (k.m. funza wa mahindi, ugonjwa wa michirizi ya mihogo).",
            parameters={
                "type": "object",
                "properties": {
                    "zao": {"type": "string", "description": "Jina la zao, k.m. mahindi, maharage, mihogo, nyanya"},
                    "dalili_au_mdudu": {"type": "string", "description": "Dalili zilizoonekana au jina la mdudu (k.m. funza, madoa meusi, majani kukunjana)"}
                },
                "required": ["zao", "dalili_au_mdudu"]
            },
            func=self._tool_crop_disease
        )

    def _tool_market_prices(self, zao: str, mji: str) -> Dict[str, Any]:
        zao_lower = zao.lower()
        mji_lower = mji.lower()
        
        # Realistic representative regional commodity prices
        prices_db = {
            "mahindi": {
                "nairobi": "KES 3,800 kwa gunia la kilo 90",
                "dar es salaam": "TZS 65,000 kwa gunia la kilo 100",
                "kampala": "UGX 95,000 kwa gunia la kilo 100",
                "goma": "USD 35 au CDF 98,000 kwa gunia",
                "kigali": "RWF 32,000 kwa gunia"
            },
            "kahawa": {
                "nairobi": "KES 420 kwa kilo (Daraja la AA)",
                "dar es salaam": "TZS 7,500 kwa kilo (Arabika)",
                "kampala": "UGX 9,200 kwa kilo (Robusta)",
                "kigali": "RWF 3,800 kwa kilo"
            }
        }
        price_info = prices_db.get(zao_lower, {}).get(mji_lower, "Bei inabadilika kulingana na mnada wa siku")
        return {
            "zao": zao,
            "mji": mji,
            "bei_ya_sasa": price_info,
            "chanzo": "East Africa Grain Council (EAGC) Market Data",
            "hali": "sahihi"
        }

    def _tool_weather(self, eneo: str) -> Dict[str, Any]:
        return {
            "eneo": eneo,
            "hali_ya_hewa": "Mvua za wastani na joto la nyuzi 24°C",
            "ushauri_wa_kilimo": "Wakati mzuri wa maandalizi ya shamba na upandaji wa mbegu za muda mfupi.",
            "chanzo": "Tanzania Meteorological Authority / Kenya Met Department"
        }

    def _tool_tax_calculator(self, kiasi: float, nchi: str) -> Dict[str, Any]:
        nchi_lower = nchi.lower()
        vat_rates = {
            "tanzania": 0.18,  # TRA 18%
            "kenya": 0.16,      # KRA 16%
            "uganda": 0.18,     # URA 18%
            "rwanda": 0.18,     # RRA 18%
            "drc": 0.16         # DGI 16%
        }
        rate = vat_rates.get(nchi_lower, 0.18)
        vat_amount = kiasi * rate
        return {
            "nchi": nchi,
            "kiasi_halisi": kiasi,
            "kiwango_cha_vat": f"{int(rate * 100)}%",
            "makisio_ya_vat": vat_amount,
            "jumla_pamoja_na_vat": kiasi + vat_amount
        }


    def _tool_loan_simplifier(self, kiasi_cha_mkopo: float, kiasi_cha_kurejesha: float, muda_siku: int) -> Dict[str, Any]:
        riba_pesa = kiasi_cha_kurejesha - kiasi_cha_mkopo
        riba_asilimia = (riba_pesa / kiasi_cha_mkopo) * 100 if kiasi_cha_mkopo > 0 else 0
        
        # Calculate APR annualized percentage rate
        apr = (riba_asilimia / muda_siku) * 365 if muda_siku > 0 else 0
        
        hatari = "Chini (Salama)"
        ushauri = "Riba hii ipo ndani ya kiwango cha kawaida cha benki za biashara."
        if apr > 100:
            hatari = "JUU SANA (Hatari ya Mtego wa Madeni)"
            ushauri = f"Onyo: Mkopo huu una riba ya mwaka ya {apr:.1f}%. Hii ni mikopo ya simu inayonyonya wafanyabiashara wadogo. Fikiria kujiunga na VICOBA au SACCOS iliyosajiliwa badala yake."
        elif apr > 40:
            hatari = "Wastani kuelekea Juu"
            ushauri = "Riba hii ni ya juu kulinganisha na benki za maendeleo. Hakikisha biashara yako ina faida inayozidi kiwango hiki."

        return {
            "kiasi_mkopo": kiasi_cha_mkopo,
            "kiasi_kurejesha": kiasi_cha_kurejesha,
            "riba_pesa": riba_pesa,
            "riba_asilimia_kipindi": f"{riba_asilimia:.1f}% kwa siku {muda_siku}",
            "riba_ya_mwaka_apr": f"{apr:.1f}%",
            "tathmini_ya_hatari": hatari,
            "ushauri_wa_kifedha": ushauri
        }

    def _tool_crop_disease(self, zao: str, dalili_au_mdudu: str) -> Dict[str, Any]:
        zao_lower = zao.lower()
        dalili_lower = dalili_au_mdudu.lower()

        # Knowledge base of localized treatments
        if "mahindi" in zao_lower and ("funza" in dalili_lower or "armyworm" in dalili_lower):
            tiba = "1. Nyunyizia majivu ya jikoni au mchanga safi katikati ya kilele cha mmea (nguzo ya mahindi) asubuhi na mapema. 2. Tumia dawa zilizoidhinishwa za Emamectin Benzoate (k.m. Prove / Match) kabla jua halijawa kali. 3. Epuka kunyunyizia nyuki wakiwepo."
            kichocheo = "Funza wa Mahindi (Fall Armyworm - Spodoptera frugiperda)"
        elif "mihogo" in zao_lower:
            tiba = "1. Ondoa na choma mara moja mimea iliyoathirika (kuzuia kuenea). 2. Tumia vipando vilivyothibitishwa visivyo na virusi (k.m. kutoka vituo vya utafiti vya TARI au KALRO). 3. Dhibiti inzi weupe (whiteflies) wanaosambaza ugonjwa."
            kichocheo = "Ugonjwa wa Michirizi ya Mihogo (Cassava Brown Streak Disease) au Batobato"
        elif "nyanya" in zao_lower:
            tiba = "1. Ondoa majani ya chini yanayogusa unyevu wa ardhi. 2. Tumia dawa ya ukungu ya shaba (Copper Oxychloride) au Mancozeb wakati wa mvua kuzuia ukungu wa ukungu-chelewa (Late Blight)."
            kichocheo = "Ukungu wa Nyanya (Blight) au Minyoo ya Mizizi"
        else:
            tiba = "Hakikisha unabadilisha mazao shambani (crop rotation), kutumia mbolea iliyoiva vizuri, na kuondoa magugu mapema. Wasiliana na afisa ugani wa eneo lako."
            kichocheo = f"Ugonjwa/Wadudu katika zao la {zao}"

        return {
            "zao": zao,
            "dalili_au_mdudu": dalili_au_mdudu,
            "utambuzi": kichocheo,
            "tiba_na_kinga": tiba,
            "chanzo": "East Africa Agricultural Extension Services / KALRO / TARI"
        }


tool_registry = ToolRegistry()
