"""
LughaLLM Pan-African Multi-Agent Orchestrator.
Natively serves Swahili speakers across Tanzania, Kenya, DRC, Uganda, Rwanda, Burundi, and regional EAC/SADC blocs.
Handles Multi-Dialect Detection (Sanifu, Sheng, Kingwana, Ugandan, Coastal) and Country-Aware Agent Routing.
"""

import re
import os
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Tuple, Optional


class DialectDetector:
    """
    Detects regional Swahili dialects and urban sociolects across East and Central Africa:
    - kiswahili_sanifu: Tanzania, Kenya standard, EAC official
    - sheng_nairobi: Kenya urban youth sociolect
    - kingwana_drc: Democratic Republic of Congo (Kivu, Katanga, Maniema, Kisangani)
    - swahili_uganda: Uganda trade and urban code-switching
    - coastal_swahili: Coastal Tanzania & Kenya (Zanzibar, Mombasa, Lamu)
    - swahili_rwanda_burundi: Great Lakes cross-border trade corridor
    """

    SHENG_MARKERS = [
        r"\bmanze\b", r"\bmbogi\b", r"\bganji\b", r"\bchapaa\b", r"\bluku\b",
        r"\brada\b", r"\bkupiga luku\b", r"\bmwizi\b", r"\bmaze\b", r"\bmsee\b",
        r"\bnduthi\b", r"\bjeshi\b", r"\bkanairo\b", r"\botile\b"
    ]

    KINGWANA_MARKERS = [
        r"\bl'argent\b", r"\bbureau\b", r"\bcarte\b", r"\bkuludia\b", r"\bmasolo\b",
        r"\bmoto\b", r"\bchauffeur\b", r"\bbina\b", r"\bkupasula\b", r"\bgoma\b",
        r"\bbukavu\b", r"\blubumbashi\b", r"\bcongo\b", r"\bdrc\b", r"\brdc\b",
        r"\bfranc congolais\b", r"\bkinshasa\b", r"\bkamalondo\b", r"\bkuloba\b"
    ]

    UGANDA_MARKERS = [
        r"\bssebo\b", r"\bnyabo\b", r"\bmatooke\b", r"\bkatale\b", r"\bkampala\b",
        r"\bmomo\b", r"\buganda\b", r"\bura\b", r"\bshillingi ya uganda\b", r"\bbodaboda\b"
    ]

    COASTAL_MARKERS = [
        r"\bkiunguja\b", r"\bkimvita\b", r"\blamu\b", r"\bmombasa\b", r"\bzanzibar\b",
        r"\bmarahaba\b", r"\bsabalkheri\b", r"\bmasalkheri\b", r"\bya rabbi\b", r"\bkisiwani\b"
    ]

    SANIFU_MARKERS = [
        r"\bkwa mujibu\b", r"\btafadhali\b", r"\bshukrani\b", r"\buhakika\b",
        r"\bmfano\b", r"\bserikali\b", r"\butaratibu\b", r"\bmaendeleo\b",
        r"\bjamhuri\b", r"\bkatiba\b", r"\bmethali\b", r"\bchuo kikuu\b"
    ]

    def detect(self, text: str) -> str:
        text_lower = text.lower()
        
        scores = {
            "kingwana_drc": sum(1 for p in self.KINGWANA_MARKERS if re.search(p, text_lower)),
            "sheng_nairobi": sum(1 for p in self.SHENG_MARKERS if re.search(p, text_lower)),
            "swahili_uganda": sum(1 for p in self.UGANDA_MARKERS if re.search(p, text_lower)),
            "coastal_swahili": sum(1 for p in self.COASTAL_MARKERS if re.search(p, text_lower)),
            "kiswahili_sanifu": sum(1 for p in self.SANIFU_MARKERS if re.search(p, text_lower))
        }

        # Find dialect with maximum score
        best_dialect, max_score = max(scores.items(), key=lambda item: item[1])
        if max_score > 0:
            return best_dialect

        return "kiswahili_general"


class DomainSpecializedAgent:
    """Base domain-specialized agent."""

    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt

    def process(self, prompt: str, dialect: str) -> str:
        raise NotImplementedError


class PanAfricanAgricultureAgent(DomainSpecializedAgent):
    """Agricultural advisor covering diverse agro-ecological zones across EAC & DRC."""

    def __init__(self):
        super().__init__(
            name="Kilimo_Advisor_PanAfrica",
            system_prompt=(
                "Wewe ni mtaalamu wa kilimo Afrika Mashariki na Kati (Tanzania, Kenya, Uganda, DRC, Rwanda, Burundi). "
                "Toa ushauri kulingana na kanda ya kijiografia, ikolojia, udongo na mbegu zilizoidhinishwa."
            )
        )

    def process(self, prompt: str, dialect: str) -> str:
        prompt_lower = prompt.lower()
        
        # DRC Context (Kivu, Katanga, Cassava/Sombe)
        if any(w in prompt_lower for w in ["congo", "kivu", "goma", "bukavu", "lubumbashi", "muhogo", "sombe"]):
            return (
                f"[Kilimo Agent - DRC & Maziwa Makuu ({dialect})]: Kulingana na ardhi yenye rutuba ya volkano Kivu na Katanga: "
                f"kuhusu '{prompt}', zingatia kupanda mihogo na mahindi kwa nafasi ifaayo, "
                f"kudhibiti ugonjwa wa batobato (cassava mosaic), na kutumia mbegu zilizothibitishwa na INERA."
            )
        # Uganda Context (Matooke, Coffee)
        elif any(w in prompt_lower for w in ["uganda", "kampala", "matooke", "kahawa"]):
            return (
                f"[Kilimo Agent - Uganda ({dialect})]: Kulingana na hali ya hewa ya Uganda na miongozo ya NARO: "
                f"kuhusu '{prompt}', hakikisha migomba ya matooke inatandazwa majani (mulching) kuzuia ukame, "
                f"na mahindi yapaliliwe wiki 2-3 baada ya kuota."
            )
        # Kenya Context (KALRO, Rift Valley, Western)
        elif any(w in prompt_lower for w in ["kenya", "nairobi", "rift valley", "western", "kalro"]):
            return (
                f"[Kilimo Agent - Kenya ({dialect})]: Kulingana na miongozo ya KALRO na KEPHIS: "
                f"kuhusu '{prompt}', tumia mbolea ya kupandia iliyothibitishwa (DAP/CAN), "
                f"zingatia msimu wa mvua za masika (Long Rains), na palilia ndani ya wiki 3."
            )
        # Default / Tanzania Context
        return (
            f"[Kilimo Agent - Afrika Mashariki ({dialect})]: Kulingana na mbinu bora za kilimo za kikanda (EAC): "
            f"kuhusu swali lako ('{prompt}'), hakikisha unaandaa shamba mapema kabla ya mvua, "
            f"kutumia mbegu zilizoidhinishwa (k.m. TOSCI/KALRO/NARO), na kupalilia ndani ya wiki 2 hadi 3 baada ya kuota."
        )


class PanAfricanFinancialAgent(DomainSpecializedAgent):
    """Financial and regulatory specialist for mobile money & statutory taxes across EAC & DRC."""

    def __init__(self):
        super().__init__(
            name="Fedha_Services_PanAfrica",
            system_prompt=(
                "Wewe ni mshauri wa masuala ya kodi na huduma za fedha Afrika Mashariki na Kati. "
                "Unajua taratibu za TRA (Tanzania), KRA (Kenya), DGI (DRC), URA (Uganda), na RRA (Rwanda)."
            )
        )

    def process(self, prompt: str, dialect: str) -> str:
        prompt_lower = prompt.lower()

        # DRC (Congo) - DGI, CDF, Airtel Money RDC, Orange Money
        if any(w in prompt_lower for w in ["congo", "drc", "rdc", "dgi", "franc", "cdf", "goma", "bukavu", "lubumbashi"]):
            return (
                f"[Fedha Agent - DRC ({dialect})]: Nchini Jamhuri ya Kidemokrasia ya Kongo (RDC): "
                f"Kuhusu '{prompt}', kodi zinasimamiwa na Direction Générale des Impôts (DGI) kwa Franc Congolais (CDF) na USD. "
                f"Kwa miamala ya Airtel Money au Orange Money, wasiliana na huduma kwa wateja au wakala rasmi ukiwa na kitambulisho."
            )
        # Kenya - KRA, KES, Safaricom M-Pesa, iTax
        elif any(w in prompt_lower for w in ["kenya", "kra", "itax", "kes", "safaricom"]):
            return (
                f"[Fedha Agent - Kenya ({dialect})]: Nchini Kenya kulingana na taratibu za KRA: "
                f"Kuhusu '{prompt}', usajili wa KRA PIN unafanyika mtandaoni kupitia mfumo wa iTax ukiwa na Kitambulisho cha Taifa. "
                f"Kuhusu M-Pesa reversal, tuma SMS ya muamala kwenda namba 456 mara moja kusimamisha malipo."
            )
        # Uganda - URA, UGX, MTN MoMo
        elif any(w in prompt_lower for w in ["uganda", "ura", "ugx", "mtn", "momo"]):
            return (
                f"[Fedha Agent - Uganda ({dialect})]: Nchini Uganda kulingana na Uganda Revenue Authority (URA): "
                f"Kuhusu '{prompt}', maombi ya TIN hufanyika mtandaoni kupitia tovuti ya URA. "
                f"Kwa muamala uliokosewa wa MTN MoMo au Airtel Money, piga 100 au tumia menyu ya simu kwa usaidizi."
            )
        # Rwanda - RRA, RWF
        elif any(w in prompt_lower for w in ["rwanda", "rra", "rwf", "kigali"]):
            return (
                f"[Fedha Agent - Rwanda ({dialect})]: Nchini Rwanda kulingana na Rwanda Revenue Authority (RRA): "
                f"Kuhusu '{prompt}', usajili wa kodi na utoaji wa risiti unafuata mifumo rasmi ya kielektroniki ya RRA kwa Faranga ya Rwanda (RWF)."
            )
        # Default / Tanzania - TRA, NIDA, TZS, Vodacom M-Pesa
        return (
            f"[Fedha Agent - Tanzania & EAC ({dialect})]: Katika masuala ya kodi na miamala: "
            f"kuhusu '{prompt}', nchini Tanzania TIN inatolewa na TRA kwa kutumia namba ya NIDA. "
            f"Kwa miamala ya simu (M-Pesa, Tigo Pesa, Airtel), tuma ujumbe kwenda huduma kwa wateja (k.m. 456) kusitisha muamala."
        )


class PanAfricanCulturalAgent(DomainSpecializedAgent):
    """Cultural and linguistic agent covering proverbs, Kingwana, Sheng, and regional literature."""

    def __init__(self):
        super().__init__(
            name="Utamaduni_Linguist_PanAfrica",
            system_prompt=(
                "Wewe ni mwanaisimu wa lugha ya Kiswahili kote barani Afrika. "
                "Unaelewa Kiswahili Sanifu, Sheng ya Kenya, Kingwana ya Kongo, na lahaja za pwani na Uganda."
            )
        )

    def process(self, prompt: str, dialect: str) -> str:
        prompt_lower = prompt.lower()

        # Kingwana (DRC) query
        if dialect == "kingwana_drc" or any(w in prompt_lower for w in ["kingwana", "congo", "l'argent", "masolo"]):
            if "l'argent" in prompt_lower or "chapaa" in prompt_lower or "ganji" in prompt_lower:
                return (
                    "Katika Kingwana cha Kongo (DRC), neno 'l'argent' au 'makuta' linamaanisha pesa/fedha. "
                    "Kingwana kinachanganya maneno ya Kifaransa na lugha za asili kama vile Lingala na Kiswahili."
                )
            return (
                f"Katika lahaja ya Kingwana (DRC): jibu la swali lako linazingatia upekee wa Kiswahili cha Kongo "
                f"kinachotumiwa Goma, Bukavu na Lubumbashi, ambacho kinatambuliwa kikatiba kama lugha ya taifa."
            )

        # Sheng (Kenya) query
        elif dialect == "sheng_nairobi" or any(w in prompt_lower for w in ["sheng", "mbogi", "ganji", "chapaa", "luku", "manze"]):
            if "chapaa" in prompt_lower or "ganji" in prompt_lower:
                return "Katika Sheng ya Nairobi, maneno 'chapaa' na 'ganji' yanamaanisha pesa au fedha taslimu."
            elif "mbogi" in prompt_lower:
                return "Neno 'mbogi' katika Sheng linamaanisha marafiki, genge, au kikundi cha watu wanaoshirikiana."
            return f"Katika muktadha wa Sheng ya Nairobi: swali lako linaangazia msamiati wa mitaani unaotumiwa na vijana."

        # Classic Methali / Proverbs
        elif "mvumilivu hula mbivu" in prompt_lower:
            return (
                "Methali 'Mvumilivu hula mbivu' (inayotambulika kote Afrika Mashariki) inafundisha umuhimu wa subira na uvumilivu. "
                "Mtu anayesubiri kwa bidii hupata matunda mazuri na mafanikio maishani."
            )
        elif "umoja ni nguvu" in prompt_lower:
            return "Methali 'Umoja ni nguvu, utengano ni udhaifu' ni mwito mkuu wa mshikamano wa kijamii na kikanda katika jumuiya ya Afrika Mashariki."

        return (
            f"Nimekuelewa vyema. Katika lugha ya Kiswahili (lahaja: {dialect}): "
            f"jibu linazingatia sarufi sanifu na utajiri wa kiisimu wa bara la Afrika."
        )


class LughaOrchestrator:
    """Master orchestrator serving all Swahili-speaking African nations."""

    def __init__(self):
        self.detector = DialectDetector()
        self.agri_agent = PanAfricanAgricultureAgent()
        self.fin_agent = PanAfricanFinancialAgent()
        self.cultural_agent = PanAfricanCulturalAgent()

    def _query_local_daemon(self, user_message: str, dialect: str, domain: str) -> Optional[str]:
        """
        Attempts inference against a local Ollama or llama-server daemon if active on localhost,
        providing true local-first LLM inference with zero cloud dependency.
        Falls back to None if the local daemon is not running.
        """
        local_url = os.getenv("LUGHALLM_LOCAL_URL", "http://127.0.0.1:11434/api/generate")
        model_name = os.getenv("LUGHALLM_LOCAL_MODEL", "lughallm")
        try:
            payload = {
                "model": model_name,
                "prompt": user_message,
                "system": (
                    f"Wewe ni LughaLLM. Lahaja iliyotambuliwa ni {dialect}, kikoa ni {domain}. "
                    "Majibu yawe kwa Kiswahili fasaha chenye staha na adabu ya kitamaduni."
                ),
                "stream": False,
                "options": {"temperature": 0.3}
            }
            req = urllib.request.Request(
                local_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("response")
        except Exception:
            return None

    def route_and_execute(self, user_message: str, forced_dialect: str = "auto") -> Dict[str, Any]:
        dialect = self.detector.detect(user_message) if forced_dialect == "auto" else forced_dialect
        msg_lower = user_message.lower()

        # Domain classification
        if any(w in msg_lower for w in ["kilimo", "mahindi", "mbolea", "kupalilia", "shamba", "mbegu", "wadudu", "mihogo", "matooke"]):
            active_agent = self.agri_agent
            domain = "agriculture"
        elif any(w in msg_lower for w in ["pesa", "m-pesa", "tra", "kra", "dgi", "ura", "rra", "tin", "kodi", "benki", "reversal", "mkopo", "franc", "momo"]):
            active_agent = self.fin_agent
            domain = "finance"
        else:
            active_agent = self.cultural_agent
            domain = "cultural_linguistic"

        # Check local-first Ollama/llama.cpp daemon first
        local_response = self._query_local_daemon(user_message, dialect, domain)
        if local_response:
            response_text = local_response
            agent_name = "LughaLLM_Local_Edge"
        else:
            response_text = active_agent.process(user_message, dialect)
            agent_name = active_agent.name

        return {
            "response": response_text,
            "detected_dialect": dialect,
            "routed_domain": domain,
            "agent_name": agent_name
        }
