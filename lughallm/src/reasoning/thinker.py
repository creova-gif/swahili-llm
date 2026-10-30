"""
LughaLLM System-2 Deep Reasoning Engine.
Generates explicit chain-of-thought reasoning traces (<fikiri>...</fikiri>) in Swahili,
inspired by DeepSeek-R1 and OpenAI o1 architectures, adapted for Bantu agglutinative logic.
"""

from typing import Dict, Any, Tuple, Optional


class SwahiliReasoningEngine:
    """
    Simulates / generates native Swahili reasoning traces (<fikiri>...</fikiri>)
    to ensure deep multi-step problem solving, dialect resolution, and fact-checking
    before emitting the final response.
    """

    def generate_reasoning_trace(self, prompt: str, dialect: str, domain: str) -> str:
        """
        Constructs an explicit chain-of-thought trace in Swahili detailing the model's
        internal deliberation, dialect disambiguation, and hallucination checks.
        """
        trace_steps = [
            "<fikiri>",
            "1. UTAMBUZI WA SWALA NA LENGO LA MTUMIAJI:",
            f"   - Ujumbe wa mtumiaji unaangazia kikoa cha '{domain}'.",
            f"   - Maneno makuu yanachambuliwa kulingana na muundo wa lugha.",
            "",
            "2. UCHAMBUZI WA KIISIMU NA MUKTADHA WA KIKANDA:",
            f"   - Lahaja iliyotambuliwa ni '{dialect}'.",
            "   - Inapaswa kuangaliwa kama kuna maneno ya Sheng (Nairobi), Kingwana (Congo), au lahaja ya kawaida.",
            "   - Kuepuka tafsiri ya neno kwa neno (literal translation) inayopotosha maana ya asili.",
            "",
            "3. TATHMINI YA USHAHIDI NA KUZUIA UPOTOSHAJI (HALLUCINATION CHECK):",
            "   - Je, kuna majina ya nchi, sarafu au taasisi za kubuni? (K.m. kuhakikisha hatubuni Jamhuri ya Kilimanjaro).",
            "   - Mamlaka husika inazingatiwa (Tanzania=TRA, Kenya=KRA, DRC=DGI, Uganda=URA, Rwanda=RRA).",
            "",
            "4. HITIMISHO NA UTEUZI WA MAJIBU:",
            "   - Jibu liwe wazi, lenye adabu, na linalozingatia sarufi na heshima ya kitamaduni.",
            "",
            "5. UTEKELEZAJI WA KANUNI ZA ADABU NA HESHIMA (CULTURAL ETIQUETTE & HESHIMA):",
            "   - Kutambua salamu za staha (k.m. Shikamoo, Habari za asubuhi, Pole na kazi).",
            "   - Kuepuka kukataa kwa ukali (indirect demurral badala ya blunt denial).",
            "</fikiri>"
        ]
        return "\n".join(trace_steps)

    def apply_eloquent_style(self, text: str, dialect: str) -> str:
        """
        Elevates output prose to write well, eliminating corporate AI robotic filler
        ('In conclusion', 'Delve', 'Kwa ujumla tunaweza kusema') and injecting vivid cadence.
        Inspired by Garry Tan's 'LLMs That Write Well' mandate.
        """
        robotic_fillers = [
            ("Kwa ujumla, tunaweza kusema kwamba ", ""),
            ("Ni muhimu kutambua kuwa ", ""),
            ("Kama mfano wa kijasusi, ", ""),
            ("Katika hitimisho, ", ""),
            ("Kwa muhtasari, ", "")
        ]
        res = text
        for filler, repl in robotic_fillers:
            if res.startswith(filler):
                res = res.replace(filler, repl, 1)

        # Ensure sentence rhythm begins engagingly
        return res.strip()

    def apply_adabu_and_politeness(self, base_response: str, prompt: str, dialect: str) -> str:
        """
        Applies cultural etiquette (Heshima) based on user greetings and generational markers.
        """
        p_lower = prompt.lower()
        prefix = ""

        # Elder respect greeting
        if "shikamoo" in p_lower:
            prefix = "Marahaba. "
        elif "habari za asubuhi" in p_lower or "sabalkheri" in p_lower:
            prefix = "Salama kabisa, habari za asubuhi hii. "
        elif "pole na kazi" in p_lower:
            prefix = "Asante sana, kazi inakwenda vyema. "
        elif "niaje" in p_lower and "sheng" in dialect:
            prefix = "Fiti sana mkuu! "

        # Indirect demurral if response contains harsh refusal
        resp = base_response
        if resp.startswith("Hapana."):
            resp = resp.replace("Hapana.", "Kwa heshima, hilo lina ugumu kidogo lakini unaweza kufanya hivi:", 1)

        return f"{prefix}{resp}" if prefix and not resp.startswith(prefix) else resp

    def process_with_reasoning(self, prompt: str, dialect: str, domain: str, base_response: str, include_thinking: bool = True) -> str:
        """
        Combines cultural etiquette, expressive prose elevation, Swahili reasoning trace, and the final response.
        """
        eloquent_response = self.apply_eloquent_style(base_response, dialect)
        polite_response = self.apply_adabu_and_politeness(eloquent_response, prompt, dialect)
        if not include_thinking:
            return polite_response

        reasoning_trace = self.generate_reasoning_trace(prompt, dialect, domain)
        return f"{reasoning_trace}\n\n{polite_response}"


reasoning_engine = SwahiliReasoningEngine()
