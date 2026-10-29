"""
USSD Channel Gateway for Feature Phones in East Africa.
Compatible with Africa's Talking and Twilio USSD session protocols.
Enables offline/low-tech access to LughaLLM for farmers and micro-merchants without internet.
"""

from typing import Dict, Any
from lughallm.src.orchestrator.agent import LughaOrchestrator


class USSDSessionManager:
    """Manages USSD menu navigation and routes queries to LughaLLM agents."""

    def __init__(self):
        self.orchestrator = LughaOrchestrator()

    def process_ussd_request(self, session_id: str, service_code: str, phone_number: str, text: str) -> str:
        """
        Processes USSD request.
        Format follows Africa's Talking standard:
        - Return starts with 'CON ' to request further user input.
        - Return starts with 'END ' to display final message and terminate session.
        """
        trimmed_text = text.strip()
        segments = trimmed_text.split("*") if trimmed_text else []

        # Level 0: Main Menu
        if not trimmed_text:
            return (
                "CON Karibu LughaLLM — Akili Bandia ya Kiswahili:\n"
                "1. Ushauri wa Kilimo (Farming)\n"
                "2. Huduma za Fedha & Kodi (TRA/M-Pesa)\n"
                "3. Methali & Utamaduni wa Lugha\n"
                "4. Maelezo ya Huduma"
            )

        # Level 1: Submenu Selection
        choice = segments[0]

        if choice == "1":  # Kilimo
            if len(segments) == 1:
                return (
                    "CON Chagua Swala la Kilimo:\n"
                    "1. Kupalilia na Mbolea ya Mahindi\n"
                    "2. Maandalizi ya Shamba Kabla ya Mvua\n"
                    "3. Andika swali lako kwa simu"
                )
            elif len(segments) == 2:
                sub_choice = segments[1]
                if sub_choice == "1":
                    return "END [Kilimo]: Palizi ya kwanza ya mahindi inatakiwa wiki 2-3 baada ya kuota. Tumia mbolea ya kukuzia (k.m. UREA au CAN) wiki ya 4 hadi 6."
                elif sub_choice == "2":
                    return "END [Kilimo]: Lima mapema mwezi 1 kabla ya mvua, choma au zika masalia kuzuia viwavi jeshi, na chagua mbegu iliyoidhinishwa na TOSCI."
                else:
                    return "CON Andika swali lako la kilimo kwa ufupi:"
            else:
                user_q = "*".join(segments[2:])
                res = self.orchestrator.agri_agent.process(user_q, "kiswahili_sanifu")
                return f"END {res[:150]}"

        elif choice == "2":  # Fedha
            if len(segments) == 1:
                return (
                    "CON Huduma za Fedha:\n"
                    "1. Jinsi ya Kurudisha Muamala (Reversal)\n"
                    "2. Kujisajili Namba ya Mlipakodi (TIN)"
                )
            elif len(segments) == 2:
                sub = segments[1]
                if sub == "1":
                    return "END [Fedha]: Tuma namba ya muamala kwenda 456 (Vodacom/Safaricom) ndani ya dakika 2 kusimamisha muamala kabla mpokeaji hajatoa fedha."
                elif sub == "2":
                    return "END [Fedha]: Tembelea tovuti ya TRA au ofisi ya karibu ukiwa na namba ya NIDA na maelezo ya biashara yako kupata TIN bure."
                else:
                    return "END Chaguo si sahihi. Jaribu tena."

        elif choice == "3":  # Methali
            if len(segments) == 1:
                return (
                    "CON Methali na Nahau:\n"
                    "1. Mvumilivu hula mbivu\n"
                    "2. Akiba haiozi\n"
                    "3. Umoja ni nguvu"
                )
            elif len(segments) == 2:
                sub = segments[1]
                if sub == "1":
                    return "END [Methali]: 'Mvumilivu hula mbivu' inafundisha kuwa mtu mwenye subira hupata matunda mazuri na mafanikio maishani."
                elif sub == "2":
                    return "END [Methali]: 'Akiba haiozi' inafundisha umuhimu wa kujiwekea akiba kwa siku za baadaye wakati wa shida."
                else:
                    return "END [Methali]: 'Umoja ni nguvu, utengano ni udhaifu' inahimiza kushirikiana ili kushinda changamoto."

        elif choice == "4":  # Maelezo
            return (
                "END LughaLLM ni miundombinu ya kwanza ya akili bandia (AI) "
                "iliyobuniwa Afrika Mashariki kutatua changamoto za mawasiliano, kilimo na biashara."
            )

        return "END Chaguo si sahihi. Piga tena menyu kuanza upya."


ussd_manager = USSDSessionManager()
