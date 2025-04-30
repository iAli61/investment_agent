1. Target Users & Key Journeys:



Primary Users: The application primarily targets novice investors who may lack deep real estate or financial analysis expertise.

Critical Tasks/Journeys:

Property Opportunity Analysis: Assessing the market value and potential rental income of a specific property. This involves leveraging the Market Data Agent and Rent Estimation Agent.

Affordability & Financial Fit Assessment: Analyzing the investor's financial situation (income, debts, savings) and current credit market conditions to determine if they can afford the property and understand the associated financial risks. This relies heavily on the Risk Analysis Agent and potentially the Document Analysis Agent (for user-uploaded financial statements).

Investment Performance & ROI Calculation: Calculating the potential Return on Investment (ROI), considering factors like purchase price, financing, operating costs, potential appreciation, and investor-specific tax benefits. This utilizes Calculation Tools driven by inputs from multiple agents and user data.

Scenario Comparison: Comparing different properties or different investment scenarios (e.g., varying down payments, financing options) side-by-side to make an informed decision. This is handled by the Scenario Management System and its Comparison Engine.

2. Core Functionalities & Interaction:



Crucial AI Agents for UI Exposure: Based on the critical journeys for novice investors, the most crucial AI agent functions to expose (directly or indirectly) are:

Market Data Agent: For property valuation and market trends.

Rent Estimation Agent: For income projections.

Risk Analysis Agent: For assessing financial viability, affordability, and investment risks tailored to the user's profile.

Strategy Agent: (Potentially less direct interaction, but informs ROI and overall recommendations).

Supporting Functions: The Document Analysis Agent (for processing user uploads like pay stubs or property listings) and the core Calculation Tools are vital but might operate more behind the scenes, surfaced through results rather than direct interaction.

User Interaction with Agents: The envisioned interaction model is a hybrid approach:

Conversational Guidance (Chat): A central chat interface, likely managed by the Manager Agent (coordinated by the Agent Orchestrator), will be the primary interaction point. It will guide the novice user step-by-step through the analysis process, ask clarifying questions, explain concepts, proactively request missing information, and summarize findings. Users can ask questions naturally.

Structured Input (Forms/Tables): For specific data entry (e.g., user's financial details for the Risk Analysis Agent, property specifics), clear, editable forms and tables will be presented. These might be surfaced within or alongside the chat interface. Users should be able to modify these inputs either directly within the forms/tables or by instructing the chat interface (e.g., "update my annual income to $X"). The architecture's Memory Management System (especially User Preferences) will help pre-fill known information and keep inputs synchronized.

Results Visualization (Dashboards): Key outputs (market value, rent estimates, ROI projections, risk scores, affordability checks) will be presented in clear, interactive dashboards or summary cards. The Real-Time Update System (using SSE) mentioned in the architecture should be leveraged here to show instant recalculations as users adjust inputs in forms/tables or via chat.

Agent Interaction Transparency: While users interact primarily with the Manager Agent via chat, the UI could subtly indicate when specialized agents (like Market Data or Risk Analysis) are being invoked to perform specific tasks, perhaps through status indicators or section headings in the results.

Scenario Management & Comparison Engine Presentation:

This should be a dedicated section or tab within the application, clearly labeled "Scenarios" or "Comparisons".

It will be managed by the Scenario Service and Scenario Repository described in the architecture.

Users should be able to:

View a list of all saved scenarios.

Create new scenarios (potentially cloning existing ones to tweak parameters).

Edit parameters within a scenario (triggering recalculations).

Delete scenarios.

Select multiple scenarios (e.g., two different properties, or the same property with different financing) to compare.

The comparison view should utilize the Comparison Engine to calculate differences and the Diff Visualization component to clearly present side-by-side metrics, highlighting key variations (e.g., ROI, cash flow, risk score) and potentially offering natural language explanations of the differences, as suggested by the architecture.

3. Product Objectives:



Main Goals:

Speed up investment decisions (through efficient data gathering and analysis).

Improve accuracy (using specialized agents, calculation tools, and broad data access).

Provide comprehensive risk assessment (tailored to the novice user).

Educate users about property investment concepts and their specific situation.

How UI Helps Achieve Objectives:

Speed: The conversational interface streamlines the process, guided data entry prevents errors, and the Real-Time Update System provides instant feedback. Autonomous data gathering by agents (leveraging Search Tools and the RAG-Enhanced Knowledge System) reduces manual research time. Flexible input methods (direct edit or chat) cater to user preference.

Accuracy: Dedicated agents (Market Data, Rent Estimation, Risk Analysis) and Calculation Tools ensure robust analysis. The RAG system provides relevant context. Clear presentation of data and assumptions in dashboards builds trust.

Risk Assessment: The Risk Analysis Agent is central. The UI must clearly present its findings (e.g., risk scores, affordability warnings, key risk factors) in an easily understandable format for novices within the dashboard/results area.

Education: The Manager Agent (via chat) is key, explaining terms, highlighting important considerations, and proactively addressing potential concerns based on the user's inputs and the analysis results drawn from the Knowledge Base Memory. Tooltips, info icons, and links to definitions within the forms and dashboards can supplement this.

4. Brand, Style, and Technical Constraints:



Brand/Style: The application should have a modern, clean, and trustworthy visual style. It needs to feel professional and data-driven, yet approachable and intuitive for novice users. Clarity and ease of navigation are paramount. (No specific brand guidelines provided).

Technical Constraints/Preferences:

While the current PoC uses Streamlit, the architecture document explicitly mentions React for client-side UI updates and Server-Sent Events (SSE) for the Real-Time Update System.

Recommendation: To achieve the desired dynamic, interactive experience (especially responsive dashboards, real-time calculations, sophisticated scenario comparison), transitioning the frontend to a framework like React (as suggested in the architecture) is likely the best practice and necessary move beyond the Streamlit PoC limitations. This aligns with the architecture's direction.


5. Desired Design Output:


A detailed written description of the proposed UI/UX, outlining key screens, components, interaction flows, and how they address the user needs and leverage the system architecture. (Conceptual sketches/wireframes could be a helpful next step following the description).