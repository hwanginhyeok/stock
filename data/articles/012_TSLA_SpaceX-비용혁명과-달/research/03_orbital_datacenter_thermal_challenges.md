# Orbital Data Center Thermal Management: Deep Technical Research

> Research date: 2026-03-02
> Sources: NASA, ESA, Starcloud/Lumen Orbit whitepaper, Per Aspera, EE Times, CNBC, Fortune, The Register, multiple academic papers

---

## 1. Heat Dissipation in Space: The Three Mechanisms

### 1.1 Conduction
- Works **only within the spacecraft structure** itself
- Heat transfers from GPU/CPU dies -> cold plates -> heat pipes -> fluid loops -> external radiators
- Materials matter: copper cold plates, Inconel 718 tubing (ISS uses this for ammonia resistance)
- Conduction **cannot reject heat to space** -- it only moves heat internally from source to radiator
- In microgravity, natural convection within fluid loops is absent, requiring **forced pumping**

### 1.2 Convection -- IMPOSSIBLE in Vacuum
- **This is THE fundamental challenge** of space thermal management
- On Earth, convection (natural + forced) accounts for the **majority** of data center cooling
  - Air cooling: fans push air over heat sinks
  - Liquid cooling: water/glycol circulated through cold plates
  - Evaporative towers: the single largest cooling mechanism for hyperscale DCs (consumes millions of gallons/day)
- In the vacuum of space: **zero air, zero fluid medium, zero convection**
- "There's nothing that can take heat away" -- Josep Miquel Jornet, Northeastern University
- Even inside a pressurized module (like ISS), the cabin air convection is minimal and insufficient for high-power compute

### 1.3 Radiation -- The ONLY Way to Reject Heat to Space
- Governed by the **Stefan-Boltzmann Law**:
  ```
  Q = epsilon * sigma * A * T^4
  ```
  Where:
  - Q = radiated power (Watts)
  - epsilon = emissivity (0 to 1; space radiators target 0.89-0.93)
  - sigma = Stefan-Boltzmann constant = 5.67 x 10^-8 W/m^2/K^4
  - A = radiator surface area (m^2)
  - T = absolute temperature (Kelvin)

- **Key insight**: Power scales with T^4, so:
  - At 300K (27C, room temp): ~460 W/m^2 (perfect blackbody)
  - At 323K (50C): ~617 W/m^2
  - At 350K (77C): ~851 W/m^2
  - At 400K (127C): ~1,452 W/m^2

- **Real-world performance** (accounting for emissivity, solar absorption, Earth albedo):
  - ISS radiators: ~166 W/m^2 effective (70 kW / ~422 m^2)
  - Typical spacecraft radiators: 100-350 W/m^2
  - Starcloud calculation for H100 at 20C: net ~633 W/m^2 (two-sided radiation, accounting for solar/albedo absorption)

---

## 2. Why "Space is Cold" is Misleading

### 2.1 The Temperature Paradox
- **Cosmic Microwave Background**: 2.7K (-270.45C) -- the "temperature of space"
- **But this does NOT mean cooling is easy**
- Space is a near-perfect vacuum -- it has essentially **no thermal mass**
- You cannot "dump" heat into vacuum like you dump heat into air or water
- The only path is **radiation**, which follows T^4 -- efficiency **drops dramatically** at lower temperatures

### 2.2 The T^4 Problem
- Radiative cooling efficiency collapses at lower temperatures:
  - At 400K: 1,452 W/m^2
  - At 300K: 460 W/m^2 (3.2x less despite only 25% lower temperature)
  - At 200K: 91 W/m^2 (16x less than 400K)
  - At 100K: 5.7 W/m^2 (255x less than 400K)
- **Implication**: Getting electronics "cold" in space is paradoxically HARDER via radiation than on Earth via convection
- On Earth, a fan + heat sink can easily dissipate 200W from a chip. In space, that same 200W requires ~0.3-0.5 m^2 of dedicated radiator surface

### 2.3 ISS Struggles with Heat BUILDUP, Not Cold
- ISS generates 75-90 kW of electrical power -- all becomes waste heat
- Yet ISS computing is **modest** by data center standards (laptops, not GPU clusters)
- The ISS External Active Thermal Control System (EATCS) uses:
  - 6 deployable radiator arrays (billboard-sized wings)
  - 24 radiator panels per loop system
  - **422 m^2 total radiator area** to reject just 70 kW
  - Pumped liquid ammonia at 8,200-8,900 lb/hr flow rate
  - Operating at 37F +/- 2F (2.8C)
- ISS radiators are **dynamically rotated** each orbit to stay in shadow
- Temperature extremes every 90 minutes: +121C (sunlight) to -157C (shadow)
- **The ISS spends more engineering effort REMOVING heat than staying warm**

### 2.4 Solar Heating Compounds the Problem
- In LEO, solar irradiance = 1,366 W/m^2 (no atmosphere to attenuate)
- 25% stronger than at Earth's surface
- Radiators in direct sunlight **absorb** heat instead of rejecting it
- Must keep radiators pointed **away from Sun** at all times
- Earth albedo adds another ~30% reflected solar on the sunlit side
- Earth itself radiates IR (~240 W/m^2) that heats the spacecraft from below

---

## 3. Specific Thermal Solutions: Proposed and Existing

### 3.1 Deployable Radiator Panels (ISS Heritage)

**ISS EATCS Specifications (flight-proven)**:
- System: Two independent ammonia loops (Loop A on S1, Loop B on P1)
- Total capacity: 70 kW (35 kW per loop)
- Radiator panels: Z-93 white coating
  - Solar absorptivity: 0.13-0.17
  - Thermal emissivity: 0.89-0.93
  - Fin efficiency: ~85%
- Ammonia temperature control: 37F +/- 2F (2.8C +/- 1.1C)
- Radiator outlet target: -40C
- Pump flow: 8,200-8,900 lb/hr per loop
- System pressure: 300 psia nominal, 500 psia max design
- Ammonia inventory: 640 lb (~290 kg) per loop
- Component mass: Pump module ~780 lb, ATA ~1,120 lb each
- Tubing: Inconel 718 (ammonia freeze/thaw + corrosion resistance)
- **25+ years of continuous operation**, proving the concept works at ~70 kW scale

### 3.2 Two-Phase Cooling Systems
- **Loop Heat Pipes (LHPs)**: Passive, capillary-driven, no moving parts
  - First space application: Russian spacecraft, 1989
  - Used on: Boeing HS 702 commsats, ICESat, Chinese FY-1C
  - Advantage: reliable, long-distance heat transport, works against gravity
- **Advanced Hybrid Two-Phase Loops**: Active pumping + passive capillary
  - Higher heat flux capacity than pure passive systems
  - Prototype testing: up to 135 cm^2 heat source removal
- **Starcloud's approach**: Two-phase cooling to reduce pumping losses, heat transferred to deployable 1m^2 black plates facing deep space

### 3.3 Liquid Droplet Radiators (LDR) -- Advanced Concept
- **Concept**: Spray billions of tiny liquid droplets into space; they radiate heat as they fly toward a collector
- **How it works**:
  - Droplet generator creates ~200 micron droplets
  - Droplets fly through vacuum (speed < 20 m/s)
  - Massive surface-area-to-mass ratio -> efficient radiation
  - Droplet collector catches them at the other end
- **Advantages**:
  - **10x lighter** than tube-and-fin radiators (order of magnitude)
  - Can radiate **several MW per square meter** (vs. hundreds of W/m^2 for panels)
  - **Immune to micrometeorite puncture** (no tubes to hole)
  - Self-healing: lost droplets simply reduce mass slightly
- **Working fluids**:
  - Low temperature (250-500K): silicone oils, Dow Corning 705
  - High temperature (500-1000K): liquid metals (Li, Sn, Ga)
  - Requirement: low vapor pressure to minimize evaporation losses
- **Status**: NASA studied extensively in 1980s-1990s (Technical Memorandum 89852)
  - Never flight-tested at scale
  - Challenges: fluid loss, contamination of spacecraft, collector alignment
  - Potentially transformative if engineering challenges solved

### 3.4 Phase-Change Materials (PCM)
- **Purpose**: Thermal energy storage buffer (absorb heat spikes, release during cool periods)
- **Primary material**: Paraffin wax
  - Non-toxic, stable chemistry, wide melt-point range
  - High heat of fusion per unit weight
  - Dependable cycling, non-corrosive, chemically inert
- **Challenge**: Poor thermal conductivity (< 1 W/m-K for paraffin)
- **Modern enhancements**: Graphene aerogels as thermal conductive networks
- **Space application**: Absorbs transient heat loads (e.g., during eclipse transitions or burst compute), reduces peak radiator sizing requirements
- **Limitation**: PCMs don't REMOVE heat -- they STORE it temporarily; still need radiators for ultimate rejection

### 3.5 Heat Pipes and Advanced Thermal Interfaces
- Standard heat pipes: sealed tubes with working fluid, capillary wick
- Variable Conductance Heat Pipes (VCHPs): adjustable thermal resistance
- Oscillating Heat Pipes (OHPs): pulsating flow, higher capacity
- Carbon nanotube thermal interfaces: near-ideal blackbody radiation
- Photonic crystal films: high emissivity (>0.8) + high solar reflectivity

### 3.6 Orientation Management
- **Critical**: Radiators must face deep space (away from Sun AND Earth)
- ISS radiators are **actively rotated** each 90-minute orbit
- Dawn-dusk sun-synchronous orbits minimize eclipse time but also keep sunlight angle consistent
- Attitude control systems must maintain radiator pointing within a few degrees
- Any misorientation = solar heating of radiators = thermal runaway risk

### 3.7 Starcloud/Lumen Orbit's Specific Approach
- **Starcloud-1** (launched Nov 2025): 60 kg satellite, single NVIDIA H100 GPU
  - First data-center-class GPU in orbit (100x more powerful than any prior space GPU)
  - 700W thermal challenge solved via proprietary radiative cooling design
  - Deployable "1m square black plates" as radiators
  - Successfully trained NanoGPT (Shakespeare corpus) and ran Google Gemma in orbit
- **Starcloud-2** (planned Oct 2026): 100x more power generation than Starcloud-1
  - GPU cluster, persistent storage, 24/7 access
  - Proprietary thermal and power systems
- **Long-term vision**: 5 GW orbital data center
  - Solar arrays: 16 km^2
  - Radiator area: ~8 km^2 (larger than Gibraltar at 6.8 km^2)
  - Structure spanning ~4 km x 4 km
- **Key claim**: 10x lower energy costs in space vs. terrestrial, 10x CO2 savings

---

## 4. Challenges Beyond Thermal

### 4.1 Radiation Damage to Electronics

**Types of radiation damage**:
- **Single Event Upsets (SEU)**: Bit flips from heavy ions -- temporary, non-destructive
  - Commercial electronics in LEO: 10^-3 to 10^-7 errors per bit-day
  - Radiation-hardened electronics: 10^-8 to 10^-11 errors per bit-day
  - **Up to 70% of in-orbit satellite failures are radiation-induced**
- **Single Event Latch-up (SEL)**: Parasitic thyristor activation -- can destroy component
- **Single Event Burnout (SEB)**: Power MOSFET destruction
- **Single Event Gate Rupture (SEGR)**: Gate oxide breakdown
- **Total Ionizing Dose (TID)**: Cumulative degradation over time
  - Ordinary server CPU: severe damage at just a few krad
  - BAE RAD750 (rad-hard): survives 200,000 to 1,000,000 rads
  - LEO below 600 km: few to tens of krad over several years (magnetosphere protection)

**Radiation sources**:
- Galactic Cosmic Rays (GCRs)
- Solar Particle Events (SPEs)
- Van Allen Belt trapped protons/electrons
- South Atlantic Anomaly (SAA) -- particularly intense region

**Vulnerable components**: SRAM cache (small transistors, high density = maximum vulnerability)

### 4.2 Micrometeorite and Debris Impacts
- Average micrometeoroid velocity: **20 km/s** relative to spacecraft
- Orbital debris velocity: **9-10 km/s** in LEO
- ISS radiators and solar panels: **many small holes** accumulated over 25+ years
- Several ISS ammonia leaks traced to suspected micrometeoroid hits
- Radiators are **especially vulnerable** -- large external surface area, thin tubing
- Erosion timescale: ~10^4 years for complete surface loss
- **A single pinhole in a radiator coolant loop can cause cascade failure**
- As of Jan 2026: ~14,500 active satellites in orbit; SpaceX wants to add 1 million more

### 4.3 Power Generation Limits
- Modern space-grade solar panels (multi-junction GaAs): ~30% efficiency, ~200 W/m^2
- **Eclipse periods in LEO**: 25-35% of each 90-minute orbit is darkness (~30 min)
- Sun-synchronous orbits: ~70-75% illumination (best case)
- **For 100 kW continuous power in LEO**:
  - Must generate ~140 kW during sunlit periods
  - Requires ~700 m^2 of solar panels
  - Panel mass: ~930 kg (at ~150 W/kg)
  - Battery storage (50 kWh for eclipse): ~500 kg (at ~100 Wh/kg)
  - Power infrastructure alone: ~1.4 metric tons
- **Degradation**: 2-3% efficiency loss per year from radiation
  - GaAs panels: 10-20% degradation in first 12 months (harsh orbits)
  - Atomic oxygen exposure: 5-15% loss in first year (LEO)
  - Design must include margin or plan for replacement every 5-7 years
- **1 GW would require ~1 km^2 of solar panels** -- extremely heavy and expensive to launch

### 4.4 Latency
- LEO at 550 km: one-way signal time ~1-4 ms
- Minimum round-trip at 550 km: **3.7 ms** (propagation only)
- Realistic RTT including processing: **20-50 ms**
- OneWeb measured: ~32 ms in actual tests
- **NOT zero latency** -- comparable to cross-continent terrestrial
- GEO (35,786 km): ~240 ms RTT (unusable for real-time AI inference)
- **Bandwidth bottleneck**: Ka-band RF = 1-3 Gbps per beam; optical = potential 100+ Gbps
  - Downloading 1 PB at 100 Gbps takes > 1 day
  - A terrestrial data hall generates that volume "before lunch"

### 4.5 Maintenance and Repair
- **Nearly all satellites are "fly-till-they-die"** -- no technician visits
- Cannot repair or replace a failed GPU, memory stick, or coolant pump
- Must be designed with **extreme fault tolerance**:
  - Triple-modular redundancy (TMR): 3 processors vote on results
  - ECC memory everywhere
  - Hot spare components
  - Autonomous failure detection and isolation
- Planned lifecycle: operate 5-7 years, deorbit, launch Version N+1
- **25-year LEO deorbiting rule** -- must carry deorbit capability (propellant, drag-sail)
- Starlink model: 5-year lifespan, 30% fuel reserved for controlled deorbit

### 4.6 Debris Risk (Kessler Syndrome)
- **Current orbital population**: ~14,500 active satellites (Jan 2026)
- SpaceX FCC filing: **up to 1 million additional satellites**
- That's a **6,800% increase** in active satellite count
- SpaceX mitigation: lowering Starlink to 480 km (from 550 km)
  - At 480 km: non-maneuvering satellite deorbits in 2-6 months
  - At 550 km: 1-3 years
  - Creates "self-cleaning" orbital regime
- Jonathan McDowell (Harvard): "One million satellites will be a big challenge for astronomy"
- Fleet of satellite servicing vehicles required to prevent cascade
- Any collision creates thousands of fragments, each a potential impactor

### 4.7 Data Sovereignty and Regulatory Issues
- **Outer Space Treaty (1967)**: Orbit is global commons, no national sovereignty
- But **terrestrial data regulations** (GDPR, ITAR) haven't been updated for orbital compute
- **Key question**: If citizen data is processed on a satellite, which country's laws apply?
  - Country of data origin?
  - State that launched the satellite?
  - Operator managing the DC?
  - Cloud provider controlling access?
- **Proposed solution**: "Digital flag state" model (like maritime law) -- registering nation governs data residency
- EU GDPR implications: US-owned satellite processing EU data over EU territory = regulatory nightmare
- Developing nations: orbital DCs could place critical infrastructure beyond regulatory reach
- **FCC/ITU spectrum allocation** for 1 million satellites = unprecedented coordination challenge

---

## 5. What Proponents Say About Each Challenge

### 5.1 Starcloud / Lumen Orbit's Position
- **Thermal**: "Use the vacuum of deep space as an infinite heat sink" via deployable radiator plates
  - Demonstrated on Starcloud-1 with single H100 (700W) -- it works
  - Two-phase cooling to minimize pumping losses
  - CTO Adi Oltean designed radiative cooling system from scratch
- **Radiation**: Using commercial-off-the-shelf (COTS) GPUs with software-level error correction
  - H100 operated successfully in LEO -- first data-center-class GPU in orbit
  - Short satellite lifespan (5 years) limits cumulative TID exposure
- **Power**: Space solar delivers 3-4x more energy than terrestrial (no atmosphere, no clouds, no night)
  - Dawn-dusk orbits maximize illumination
- **Cost**: Claims 10x lower energy costs, launch costs declining with Starship
- **CEO Philip Johnston**: "Nearly all new data centers will be being built in outer space" within 10 years
- **NVIDIA backing**: Inception program member; running Gemma in orbit validates GPU compute path
- **Starcloud-2**: "Will generate more cash than it costs to build and launch"

### 5.2 ISS 25+ Years of Thermal Heritage
- EATCS has operated continuously for decades
- Proven: ammonia loops + deployable radiators work reliably at 70 kW scale
- Ammonia leaks have occurred (micrometeoroid suspected) -- repaired by EVA
- System is over-designed with dual redundant loops
- **But**: ISS thermal load is orders of magnitude below what a real data center needs
- Scaling from 70 kW to 1 MW or 1 GW is a **qualitative, not just quantitative** challenge

### 5.3 Radiation-Hardened vs. COTS with Redundancy
- **Rad-hard approach**: Proven but **10-100x more expensive** and 5-10 years behind in performance
  - BAE RAD750: survives 1 Mrad but runs at ~200 MHz
  - Completely inadequate for AI/ML workloads
- **COTS + redundancy approach** (what Starcloud is doing):
  - Use latest commercial GPUs (H100, Blackwell)
  - Accept higher SEU rate
  - Mitigate with ECC, TMR, checkpoint/restart
  - Short satellite lifespan limits cumulative dose
  - **Replace rather than harden** -- Starlink model applied to compute
- **SpaceX philosophy**: Cheap launches make satellites disposable
  - If a GPU fails from radiation, deorbit the satellite and launch a new one
  - Cost of launch << cost of radiation hardening every component
  - 5-year refresh cycle also upgrades to latest silicon generation

### 5.4 SpaceX / Elon Musk's Position (as of Feb 2026)
- **Musk quote** (Feb 2026): "You can mark my words, in 36 months but probably closer to 30 months, the most economically compelling place to put AI will be space"
- **Musk prediction**: "Five years from now... we will launch and be operating every year more AI in space than the cumulative total on Earth"
- **SpaceX FCC filing**: Up to 1 million data center satellites at 500-2,000 km altitude
- **SpaceX-xAI merger**: Combined valuation ~$1.25 trillion; orbital DC as strategic rationale
- **Technical approach**: "Simply scaling up Starlink V3 satellites, which have high-speed laser links, would work. SpaceX will be doing this." -- Musk
- **Starship enabling**: ~100 metric tons to LEO per launch at projected costs of $10-20M/launch
- FCC filing references "becoming a Kardashev II-level civilization" and "surpassing U.S. electricity consumption"
- 60 high-capacity Starlink V3 satellites per Starship flight starting 2026

### 5.5 Expert Skepticism
- **Kathleen Curlee** (Georgetown CSET): "This is something people are cynical about because it's just technologically not feasible"
- **Jeff Thornburg** (Portal Space, ex-SpaceX): "Minimum 3-5 years before something working properly... mass production unlikely before 2030"
- **Josep Miquel Jornet** (Northeastern): "Two to three years is not realistic at the scale being promised"
- **Deutsche Bank**: Competitive orbital DC "well into the 2030s"
- **ESPI Report**: Competitive power-equivalent DC "at least 20 years away"
- **Jonathan McDowell** (Harvard): Feasibility "unclear at this stage"; million-satellite debris concern

---

## 6. First Principles: Earth DC vs. Space DC

### 6.1 Earth Data Center Environment
| Factor | Earth Advantage | Earth Constraint |
|--------|----------------|-----------------|
| **Cooling** | Abundant air (convection), water (liquid cooling), gravity (natural convection) | Water scarcity increasing; 110M-1.8B gal/year per DC |
| **Power** | Established grid, nuclear, natural gas | Grid constraints, permitting delays (2-5 years), 30-40% of DC cost |
| **Land** | Construction technology mature | NIMBY opposition, zoning restrictions, limited sites near power |
| **Maintenance** | Technicians available 24/7 | Labor costs, training |
| **Bandwidth** | Fiber optic = practically unlimited | Dependent on fiber build-out |
| **Regulations** | Clear legal frameworks | GDPR, data residency requirements, export controls |
| **PUE** | Best: 1.1-1.2 | Cooling overhead = 10-60% of total power |
| **Water** | Evaporative cooling highly efficient | 1.8 liters per kWh (industry average) |
| **Environment** | Proven, reliable, decades of experience | Carbon emissions, water consumption, land use |

### 6.2 Space Data Center Environment
| Factor | Space Advantage | Space Constraint |
|--------|----------------|-----------------|
| **Cooling** | Unlimited "cold sink" (2.7K background) | ONLY via radiation; no convection; ~460 W/m^2 at 300K |
| **Power** | Free solar energy 1,366 W/m^2, no permitting | Eclipse periods (25-35%), panel degradation (2-3%/yr), massive panel area |
| **Land** | No land constraints, no NIMBY | Must be in stable orbit; debris risk; spectrum allocation |
| **Maintenance** | None needed (or impossible) | Cannot repair; must design for total redundancy |
| **Bandwidth** | Laser inter-satellite links | Ground downlink bottleneck; 1-3 Gbps RF, maybe 100 Gbps optical |
| **Regulations** | Outer Space Treaty = fewer restrictions? | Regulatory vacuum; data sovereignty unclear; FCC/ITU approval |
| **PUE** | Potentially very low (no chillers, no fans) | All infrastructure must be launched; mass = cost |
| **Water** | Zero water consumption | N/A |
| **Environment** | No carbon at operation (solar powered) | Launch emissions; debris; astronomical light pollution |

### 6.3 The Core Math Problem
- **1 MW data center on Earth**: Standard facility, PUE ~1.3, ~50,000 sq ft, built in 12-18 months
- **1 MW data center in Space**:
  - Radiator area: ~1,200 m^2 (35m x 35m) minimum
  - Solar panel area: ~5,000-7,000 m^2 (at 70% illumination duty)
  - Total structure mass: 30-50 metric tons (compute + power + thermal + structure)
  - Launch cost at $200/kg (Starship aspirational): $6-10M per MW launched
  - Launch cost at current $2,000/kg: $60-100M per MW launched
  - Assembly: requires on-orbit robotics or EVA
  - Lifespan: 5-7 years before deorbit and replacement
- **Scaling to 1 GW**: Multiply everything by 1,000
  - 1.2 km^2 of radiators
  - 5-7 km^2 of solar panels
  - 30,000-50,000 metric tons to orbit
  - At $200/kg: $6-10 BILLION just in launch costs
  - At current rates: $60-100 BILLION

### 6.4 The Starship Variable
- **Everything changes if** Starship achieves:
  - $10-20M per 100-ton launch ($100-200/kg)
  - Rapid reusability (daily launches)
  - Reliable deployment of massive structures
- SpaceX's thesis: launch cost reduction makes orbital DC economics work
- Counter-argument: even at $100/kg, the radiator/panel mass problem remains
- **The real bottleneck isn't launch cost -- it's the physics of radiative cooling**

---

## 7. Additional Players and Timeline

### 7.1 Axiom Space + Spacebilt
- Planned: Orbital Data Center Node on ISS by **2027**
- Skyloom providing optical terminal (SDA Tranche 1 compatible)
- Initial: 2.5 Gbps connectivity, roadmap to 100 Gbps
- Plan for 3+ interconnected ODC nodes by 2027
- Partners: Phison Electronics, Microchip Technology
- Focus: national security, commercial, and international customers

### 7.2 Timeline Summary
| Date | Milestone |
|------|-----------|
| Nov 2025 | Starcloud-1 launched (1x H100 GPU in orbit) |
| Dec 2025 | First LLM (NanoGPT) trained in space; Gemma run in orbit |
| Jan 2026 | SpaceX files FCC application for 1M satellite constellation |
| Feb 2026 | SpaceX-xAI merger announced ($1.25T combined valuation) |
| Oct 2026 | Starcloud-2 planned launch (100x power of SC-1, GPU cluster) |
| 2026 | SpaceX begins launching Starlink V3 via Starship (60 sats/flight) |
| 2027 | Axiom/Spacebilt ODC node on ISS |
| 2028-2029 | Musk's "cost parity" prediction window |
| 2030+ | Expert consensus: earliest realistic scale deployment |
| 2035+ | Deutsche Bank: "close to parity" |
| 2045+ | ESPI: competitive power-equivalent DC |

---

## Sources

- [Per Aspera - Realities of Space-Based Compute](https://www.peraspera.us/realities-of-space-based-compute/)
- [Mikhail Klassen - Orbital Data Centers](https://www.mikhailklassen.com/posts/orbital-data-centers/orbital-data-centers/)
- [NVIDIA Blog - How Starcloud Is Bringing Data Centers to Outer Space](https://blogs.nvidia.com/blog/starcloud/)
- [CNBC - Nvidia-backed Starcloud trains first AI model in space](https://www.cnbc.com/2025/12/10/nvidia-backed-starcloud-trains-first-ai-model-in-space-orbital-data-centers.html)
- [The Register - FCC opens Musk's 1M-satellite DC plan](https://www.theregister.com/2026/02/05/spacex_1m_satellite_datacenter/)
- [Fortune - AI data centers in space: Experts say not so fast](https://fortune.com/2026/02/19/ai-data-centers-in-space-elon-musk-power-problems/)
- [SpaceNews - Cost-driven strategies for space-based data centers](https://spacenews.com/beyond-the-horizon-cost-driven-strategies-for-space-based-data-centers/)
- [NASA - ISS ATCS Overview (PDF)](https://www.nasa.gov/wp-content/uploads/2021/02/473486main_iss_atcs_overview.pdf)
- [Grokipedia - ISS External Active Thermal Control System](https://grokipedia.com/page/External_Active_Thermal_Control_System)
- [Wikipedia - Liquid Droplet Radiator](https://en.wikipedia.org/wiki/Liquid_droplet_radiator)
- [Wikipedia - Stefan-Boltzmann Law](https://en.wikipedia.org/wiki/Stefan%E2%80%93Boltzmann_law)
- [Wikipedia - Single-event Upset](https://en.wikipedia.org/wiki/Single-event_upset)
- [NASA - Spacecraft Thermal Control SOA](https://www.nasa.gov/smallsat-institute/sst-soa/thermal-control/)
- [Starcloud Whitepaper - Why We Should Train AI in Space](https://starcloudinc.github.io/wp.pdf)
- [Singularity Hub - Future Data Centers Could Orbit Earth](https://singularityhub.com/2025/11/03/future-data-centers-could-orbit-earth-powered-by-the-sun-and-cooled-by-the-vacuum-of-space/)
- [Axiom Space - Orbital Data Center Node on ISS](https://www.axiomspace.com/release/axiom-space-spacebilt-announce-orbital-data-center-node)
- [Blocksandfiles - Starcloud pitches orbital datacenters](https://blocksandfiles.com/2025/10/23/starcloud-orbiting-datacenters/)
- [Rest of World - Who will regulate data centers in space?](https://restofworld.org/2026/orbital-data-centers-ai-sovereignty/)
- [Bloomberg Law - Digital Flag State Rule](https://news.bloomberglaw.com/legal-exchange-insights-and-commentary/digital-flag-state-rule-would-give-space-law-a-regulatory-boost)
- [Hackaday - Space-Based Datacenters Take The Cloud Into Orbit](https://hackaday.com/2025/06/19/space-based-datacenters-take-the-cloud-into-orbit/)
- [NASA NTRS - Liquid Droplet Radiator Technical Memorandum](https://ntrs.nasa.gov/api/citations/19870010920/downloads/19870010920.pdf)
- [ScienceDirect - Phase change materials in space systems](https://www.sciencedirect.com/science/article/abs/pii/S0094576523006707)
- [SpaceX lowering Starlink to cut collision risks](https://www.technology.org/2026/01/02/spacex-lowers-starlink-satellites-closer-to-earth-to-cut-collision-risks/)
- [DCD - Lumen Orbit rebrands to Starcloud](https://www.datacenterdynamics.com/en/news/lumen-orbit-rebrands-to-starcloud-raises-another-10m-for-in-orbit-data-centers/)
- [Starcloud-1 official page](https://www.starcloud.com/starcloud-1)
