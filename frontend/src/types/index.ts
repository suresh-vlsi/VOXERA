
export interface VocabularyDomain {
  id: string;
  label: string;
  description: string;
  terms: string[];
}

export const vocabularyDomains: VocabularyDomain[] = [
  {
    id: "digital_design",
    label: "Digital Design & RTL",
    description: "Hardware description languages and digital logic",
    terms: [
      "FIFO", "LIFO", "RTL", "Verilog", "SystemVerilog", "ASIC",
      "FPGA", "FSM", "Multiplexer", "Demultiplexer", "Flip-flop",
      "Latch", "Synchronous reset", "Asynchronous reset", "Active-low reset",
    ],
  },
  {
    id: "verification",
    label: "Design Verification",
    description: "Verification methodologies and test generation",
    terms: [
      "UVM", "SVA", "Assertion", "Coverage", "Constrained random",
      "Scoreboard", "Testbench", "ATPG", "PODEM", "D-algorithm",
    ],
  },
  {
    id: "protocols",
    label: "Communication Protocols",
    description: "Common digital communication interfaces",
    terms: ["UART", "SPI", "I2C", "AXI", "AHB", "APB"],
  },
  {
    id: "physical_design",
    label: "VLSI CAD & Physical Design",
    description: "Synthesis, timing and physical implementation",
    terms: [
      "Yosys", "Verilator", "Icarus Verilog", "GTKWave", "OpenROAD",
      "Placement", "Routing", "Static timing analysis", "STA", "DRC",
      "LVS", "SDC", "UPF", "Clock tree synthesis",
    ],
  },
  {
    id: "semiconductor",
    label: "Semiconductor Devices",
    description: "MOS devices and semiconductor physics",
    terms: [
      "MOSFET", "CMOS", "DIBL", "Threshold voltage",
      "Channel length modulation", "Body effect", "Subthreshold leakage",
    ],
  },
  {
    id: "formal_methods",
    label: "Formal Methods",
    description: "Boolean reasoning and formal verification",
    terms: ["BDD", "SAT", "CNF", "Equivalence checking", "Boolean derivative"],
  },
];
