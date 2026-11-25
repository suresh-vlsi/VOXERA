
"""
VOXERA Technical Vocabulary Engine
==================================

Maintains domain-specific engineering terminology and converts
selected entries into Sarvam Dictate's vocabulary format.

Sarvam entry format:
{
    "word": "FIFO",
    "sounds_like": ["fee-fo"],
    "description": "First-in first-out hardware buffer"
}

Important:
- Only include terms relevant to the current recording.
- Do not create ambiguous phonetic substitutions.
- Maximum 1000 entries per request.
"""

from dataclasses import dataclass
from typing import Iterable
import re
import unicodedata


MAX_SARVAM_TERMS = 1000


@dataclass(frozen=True, slots=True)
class VocabularyTerm:
    """Represents one canonical engineering term."""

    word: str
    domain: str
    description: str = ""
    sounds_like: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.word.strip():
            raise ValueError("Vocabulary word cannot be empty.")

        if not self.domain.strip():
            raise ValueError("Vocabulary domain cannot be empty.")

        if any(not alias.strip() for alias in self.sounds_like):
            raise ValueError(
                f"Empty pronunciation alias for {self.word}"
            )


# ---------------------------------------------------------
# 1. ENGINEERING VOCABULARY DATABASE
# ---------------------------------------------------------

VOCABULARY: tuple[VocabularyTerm, ...] = (

    # DIGITAL DESIGN AND RTL
    VocabularyTerm("FIFO", "digital_design",
                   "First-in first-out hardware buffer"),

    VocabularyTerm("LIFO", "digital_design",
                   "Last-in first-out hardware buffer"),

    VocabularyTerm("RTL", "digital_design",
                   "Register transfer level"),

    VocabularyTerm("Verilog", "digital_design",
                   "Hardware description language"),

    VocabularyTerm("SystemVerilog", "digital_design",
                   "Hardware design and verification language"),

    VocabularyTerm("ASIC", "digital_design",
                   "Application-specific integrated circuit"),

    VocabularyTerm("FPGA", "digital_design",
                   "Field-programmable gate array"),

    VocabularyTerm("FSM", "digital_design",
                   "Finite state machine"),

    VocabularyTerm("Multiplexer", "digital_design",
                   "Digital data selector"),

    VocabularyTerm("Demultiplexer", "digital_design",
                   "Digital data distributor"),

    VocabularyTerm("Flip-flop", "digital_design",
                   "Sequential logic storage element"),

    VocabularyTerm("Latch", "digital_design",
                   "Level-sensitive storage element"),

    VocabularyTerm("Synchronous reset", "digital_design",
                   "Clock-synchronized reset"),

    VocabularyTerm("Asynchronous reset", "digital_design",
                   "Reset independent of clock"),

    VocabularyTerm("Active-low reset", "digital_design",
                   "Reset asserted by logic zero"),

    # VERIFICATION
    VocabularyTerm("UVM", "verification",
                   "Universal Verification Methodology"),

    VocabularyTerm("SVA", "verification",
                   "SystemVerilog Assertions"),

    VocabularyTerm("Assertion", "verification",
                   "Property checking in hardware verification"),

    VocabularyTerm("Coverage", "verification",
                   "Verification completeness measurement"),

    VocabularyTerm("Constrained random", "verification",
                   "Constraint-driven stimulus generation"),

    VocabularyTerm("Scoreboard", "verification",
                   "Expected-versus-actual result checker"),

    VocabularyTerm("Testbench", "verification",
                   "Hardware verification environment"),

    VocabularyTerm("ATPG", "verification",
                   "Automatic test pattern generation"),

    VocabularyTerm("PODEM", "verification",
                   "Path-oriented decision making ATPG algorithm"),

    VocabularyTerm("D-algorithm", "verification",
                   "Automatic test pattern generation algorithm"),

    # COMMUNICATION PROTOCOLS
    VocabularyTerm("UART", "protocols",
                   "Universal asynchronous receiver transmitter"),

    VocabularyTerm("SPI", "protocols",
                   "Serial peripheral interface"),

    VocabularyTerm("I2C", "protocols",
                   "Inter-integrated circuit protocol"),

    VocabularyTerm("AXI", "protocols",
                   "Advanced extensible interface"),

    VocabularyTerm("AHB", "protocols",
                   "Advanced high-performance bus"),

    VocabularyTerm("APB", "protocols",
                   "Advanced peripheral bus"),

    # VLSI CAD AND PHYSICAL DESIGN
    VocabularyTerm("Yosys", "physical_design",
                   "Open-source RTL synthesis framework"),

    VocabularyTerm("Verilator", "physical_design",
                   "Verilog and SystemVerilog simulator"),

    VocabularyTerm("Icarus Verilog", "physical_design",
                   "Verilog simulation tool"),

    VocabularyTerm("GTKWave", "physical_design",
                   "Digital waveform viewer"),

    VocabularyTerm("OpenROAD", "physical_design",
                   "Open-source physical design tool"),

    VocabularyTerm("Placement", "physical_design",
                   "Standard cell placement"),

    VocabularyTerm("Routing", "physical_design",
                   "Physical interconnection routing"),

    VocabularyTerm("Static timing analysis", "physical_design",
                   "Timing verification without simulation"),

    VocabularyTerm("STA", "physical_design",
                   "Static timing analysis"),

    VocabularyTerm("DRC", "physical_design",
                   "Design rule checking"),

    VocabularyTerm("LVS", "physical_design",
                   "Layout versus schematic verification"),

    VocabularyTerm("SDC", "physical_design",
                   "Synopsys design constraints"),

    VocabularyTerm("UPF", "physical_design",
                   "Unified power format"),

    VocabularyTerm("Clock tree synthesis", "physical_design",
                   "Clock distribution network synthesis"),

    # SEMICONDUCTOR DEVICES
    VocabularyTerm("MOSFET", "semiconductor",
                   "Metal oxide semiconductor field effect transistor"),

    VocabularyTerm("CMOS", "semiconductor",
                   "Complementary metal oxide semiconductor"),

    VocabularyTerm("DIBL", "semiconductor",
                   "Drain-induced barrier lowering"),

    VocabularyTerm("Threshold voltage", "semiconductor",
                   "MOS transistor threshold voltage"),

    VocabularyTerm("Channel length modulation", "semiconductor",
                   "MOSFET output conductance effect"),

    VocabularyTerm("Body effect", "semiconductor",
                   "Threshold voltage dependence on body bias"),

    VocabularyTerm("Subthreshold leakage", "semiconductor",
                   "Current below threshold voltage"),

    # BOOLEAN LOGIC AND FORMAL METHODS
    VocabularyTerm("BDD", "formal_methods",
                   "Binary decision diagram"),

    VocabularyTerm("SAT", "formal_methods",
                   "Boolean satisfiability problem"),

    VocabularyTerm("CNF", "formal_methods",
                   "Conjunctive normal form"),

    VocabularyTerm("Equivalence checking", "formal_methods",
                   "Formal comparison of circuit behaviour"),

    VocabularyTerm("Boolean derivative", "formal_methods",
                   "Boolean sensitivity with respect to a variable"),
)


# ---------------------------------------------------------
# 2. NORMALIZATION UTILITIES
# ---------------------------------------------------------

def normalize_term(value: str) -> str:
    """Normalize text for duplicate and collision checking."""

    value = unicodedata.normalize("NFKC", value)
    value = value.strip().casefold()
    value = re.sub(r"\s+", " ", value)

    return value


# ---------------------------------------------------------
# 3. CATALOGUE VALIDATION
# ---------------------------------------------------------

def validate_catalog(
    catalog: Iterable[VocabularyTerm] = VOCABULARY,
) -> None:
    """
    Validate the vocabulary database.

    Detects:
    - Duplicate canonical words.
    - Empty aliases.
    - Ambiguous aliases assigned to different words.
    """

    seen_words: dict[str, str] = {}
    seen_aliases: dict[str, str] = {}

    for term in catalog:

        normalized_word = normalize_term(term.word)

        if normalized_word in seen_words:
            raise ValueError(
                f"Duplicate vocabulary word: {term.word}"
            )

        seen_words[normalized_word] = term.word

        for alias in term.sounds_like:

            normalized_alias = normalize_term(alias)

            if not normalized_alias:
                raise ValueError(
                    f"Empty alias for {term.word}"
                )

            existing = seen_aliases.get(normalized_alias)

            if existing and existing != normalized_word:
                raise ValueError(
                    f"Ambiguous alias '{alias}' assigned to "
                    f"'{existing}' and '{term.word}'."
                )

            seen_aliases[normalized_alias] = normalized_word


# ---------------------------------------------------------
# 4. DOMAIN DISCOVERY
# ---------------------------------------------------------

def available_domains() -> list[str]:
    """Return all available vocabulary domains."""

    return sorted({
        term.domain for term in VOCABULARY
    })


# ---------------------------------------------------------
# 5. SEARCH ENGINE
# ---------------------------------------------------------

def search_vocabulary(
    query: str,
    catalog: Iterable[VocabularyTerm] = VOCABULARY,
) -> list[VocabularyTerm]:
    """Search canonical words, descriptions and aliases."""

    query = normalize_term(query)

    if not query:
        return []

    results = []

    for term in catalog:

        searchable = [
            term.word,
            term.description,
            term.domain,
            *term.sounds_like,
        ]

        if any(
            query in normalize_term(value)
            for value in searchable
        ):
            results.append(term)

    return results


# ---------------------------------------------------------
# 6. SELECT RELEVANT TERMS
# ---------------------------------------------------------

def select_vocabulary(
    domains: Iterable[str] | None = None,
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
    catalog: Iterable[VocabularyTerm] = VOCABULARY,
) -> list[VocabularyTerm]:
    """
    Select terms using domains and explicit word selections.

    Selection is case-insensitive.
    """

    catalog = tuple(catalog)

    selected_domains = (
        {normalize_term(d) for d in domains}
        if domains is not None
        else None
    )

    included = (
        {normalize_term(w) for w in include}
        if include is not None
        else set()
    )

    excluded = (
        {normalize_term(w) for w in exclude}
        if exclude is not None
        else set()
    )

    known_words = {
        normalize_term(term.word) for term in catalog
    }

    unknown = included - known_words

    if unknown:
        raise ValueError(
            f"Unknown vocabulary terms: {sorted(unknown)}"
        )

    results = []

    for term in catalog:

        word = normalize_term(term.word)

        domain_match = (
            selected_domains is None
            or normalize_term(term.domain) in selected_domains
        )

        explicit_match = word in included

        if (domain_match or explicit_match) and word not in excluded:
            results.append(term)

    return results


# ---------------------------------------------------------
# 7. SARVAM ADAPTER
# ---------------------------------------------------------

def build_sarvam_vocabulary(
    domains: Iterable[str] | None = None,
    include: Iterable[str] | None = None,
    exclude: Iterable[str] | None = None,
    max_terms: int = 100,
    catalog: Iterable[VocabularyTerm] = VOCABULARY,
) -> list[dict[str, object]]:
    """
    Convert selected terms to Sarvam Dictate vocabulary format.

    Sarvam expects a list of objects, not a list of strings.
    """

    if not 1 <= max_terms <= MAX_SARVAM_TERMS:
        raise ValueError(
            f"max_terms must be between 1 and "
            f"{MAX_SARVAM_TERMS}."
        )

    selected = select_vocabulary(
        domains=domains,
        include=include,
        exclude=exclude,
        catalog=catalog,
    )

    if len(selected) > max_terms:
        raise ValueError(
            f"Selected {len(selected)} terms, exceeding "
            f"the configured limit of {max_terms}. "
            "Narrow the selected domains."
        )

    payload = []

    for term in selected:

        entry: dict[str, object] = {
            "word": term.word,
        }

        if term.sounds_like:
            entry["sounds_like"] = list(term.sounds_like)

        if term.description:
            entry["description"] = term.description

        payload.append(entry)

    return payload


# ---------------------------------------------------------
# 8. INITIAL SELF-VALIDATION
# ---------------------------------------------------------

validate_catalog()
