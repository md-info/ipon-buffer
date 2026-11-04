# Ipon Buffer: stakeholder presentation script

November 4, 2026
Ten-minute target. Approximately 150–160 words per minute, including short transitions. Rehearse to adjust pacing.

## 1. Title (0:00–0:10)

Ipon Buffer brings local price sharing and emergency savings into the e-wallet customers already use.

## 2. Mika knows her budget. She does not know local prices. (0:10–1:07)

Consider Mika, a fictional customer with two thousand pesos in her everyday wallet. She needs to cover groceries and household expenses, while gradually building an emergency fund. She understands the importance of saving. Her immediate challenge is knowing where she can reduce spending without giving up essentials.

Local prices are difficult to compare. A lower price may be available nearby, but discovering it means visiting several shops, asking around, or searching through scattered posts. That effort has a cost, particularly when transport and time are limited.

Even after finding a better price, Mika faces another decision: how much can she put aside while keeping enough for upcoming expenses?

Ipon Buffer addresses these connected decisions. It brings community price information into the same experience as a reviewed savings plan. That puts saving alongside the purchases customers already have to make.

## 3. Ipon Buffer (1:07–2:04)

Ipon Buffer is a community price-sharing and emergency-savings feature designed to operate within an existing e-wallet.

Customers can discover prices for local essentials, contribute their own findings, and confirm information reported by other shoppers. Alongside that activity, a savings engine recommends a contribution based on the customer's reviewed expenses and available balance. The customer decides whether to make the deposit.

For a wallet operator, the opportunity is to extend the app's role in everyday financial decisions. Payments capture the transaction itself. Price discovery gives customers a reason to engage earlier, when they are deciding where to shop and how much to spend.

The service would use the wallet's existing customer and merchant relationships. Commercially, Ipon Buffer would be offered through software licensing, integration services, and potentially merchant-funded campaigns. For the customer, the purpose is simple: build an emergency fund while keeping everyday needs covered.

## 4. Price reports customers can check (2:04–3:01)

The customer journey begins with a single screen. A compact banner shows the emergency buffer, followed by a feed of local price reports. Each report identifies the product, quantity, store and observed price. Those details matter because an apparently cheaper product may simply come in a smaller pack.

Customers can open a report, inspect its details, and confirm the price after checking it themselves. They can also contribute a photo and their own finding. Appreciation acknowledges a helpful contribution; confirmation provides a separate signal about the reported price.

The savings workflow then asks the customer to review their expenses. The engine calculates a contribution, and one explicit confirmation completes the deposit. The customer sees a receipt rather than an immediate request for another contribution.

The prototype demonstrates this with synthetic balances. Community reports inform shopping decisions, while changes to the financial plan and deposits require the customer's approval.

## 5. AI helps customers describe expenses (3:01–3:58)

AI supports the planning experience by reducing the effort required to describe expenses. A customer can explain an upcoming payment in ordinary language, and the model proposes details for the plan. The customer checks those details before accepting them.

The review matters because the model can make mistakes. An expense description may omit a due date, or the model may misunderstand whether a cost is already included in the daily budget. Making those assumptions visible gives the customer an opportunity to correct them.

The financial calculation runs separately. Rules calculate the contribution using exact amounts in centavos and account for planned essentials. The AI cannot execute transfers.

For a wallet partner, the responsibilities are clear: language assistance helps customers complete the plan, and financial rules govern the recommendation. The current demonstration uses a local model on the computer, with manual planning available as well. The benefit we intend to test is easier plan completion without reducing customer control.

## 6. A focused combination (3:58–4:55)

Our opportunity is to help with a decision customers make before they pay. Community price reporting is established in products such as GasBuddy. Venmo also combines social recommendations with commercial offers and cashback. These are useful references for understanding customer expectations.

Ipon Buffer focuses on the relationship between local essential spending and emergency saving. Customers can discover a relevant price, assess its credibility through community feedback, and review what they can contribute to their buffer within the same experience.

The Venmo comparison captures one part of that distinction: Venmo makes payments social. Ipon Buffer makes local price knowledge social and connects it to emergency savings.

Whether that is a better experience has to be tested. A pilot should establish whether this combination produces useful repeat visits and sustained buffer growth. Local relevance and reliable contributions could become an advantage over time, but the prototype does not yet establish a defensible network or superior performance.

## 7. A useful action earns a social response (4:55–5:52)

The engagement mechanism starts with a recurring customer need: buying essentials. That gives the feed a practical reason to exist before any rewards are introduced.

The design then reduces the effort involved in participating. A photo, product details and a short price report are easier to contribute than a lengthy review. Other customers can acknowledge the finding or independently confirm it. The contributor receives recognition and contribution points, making their participation visible.

This follows the motivation, ability and prompt framework described by BJ Fogg. The shopping need provides motivation, simple actions improve ability, and relevant information inside the wallet provides the prompt.

We want customers to keep sharing information that others can use. Rewards therefore need to favour information quality rather than posting volume or additional spending. In a pilot, we would examine whether recognition improves the supply of accurate reports and whether customers continue participating after the initial novelty wears off. That is the test of a sustainable community.

## 8. Revenue within the wallet business (5:52–6:49)

We would charge for the software and for merchant campaign services. A wallet operator could pay a licence fee for the software, with integration and ongoing support priced according to the deployment. Merchant-funded campaigns could provide an additional service revenue stream.

For example, a grocery merchant might fund cashback on a qualifying essentials purchase. The customer receives a tangible benefit, and the merchant pays for access to a relevant audience. A campaign fee would need a clear basis, such as an agreed service charge or a qualifying redemption, with responsibilities defined in the partner contract.

The prototype simulates purchases, campaign budgets and cashback transfers into the buffer. Production economics would also need to account for refunds, abuse, support and moderation.

Referrals to suitable savings or investment products could be considered separately. Interest income is dependent on the partner's product arrangements. The initial business case should therefore stand on licensing and campaign economics, rather than assumed returns from customer balances.

## 9. The partner buys measurable outcomes (6:49–7:46)

For a wallet partner, the question is whether the feature creates enough additional value to justify its cost and operational complexity.

The partner would need to see benefits for its business and its customers. Commercially, we would examine repeat usage, retention and additional merchant activity. For customers, we would examine completed savings contributions and buffer balances after withdrawals, while checking that planned essentials remain covered.

We also need to understand what caused the results. A purchase following an offer may have happened anyway. More visits may reflect a useful service, or simply curiosity during launch. A suitable comparison group would help separate those effects.

The pilot should also track operating costs, including report moderation, customer support and campaign abuse. A feature can attract attention while remaining expensive to sustain.

The investment decision would depend on whether the resulting customer and merchant benefits exceed those costs. Those findings would determine whether the partner renews the service or expands it.

## 10. A feature on top of the wallet (7:46–8:43)

Ipon Buffer is intended to sit within an existing wallet and its business structure. GCash and Maya illustrate the type of prospective partner; neither is currently involved.

The wallet would retain control of customer identity, balances, payment authorisation and merchant settlement. Ipon Buffer would provide the community price experience and savings guidance through agreed interfaces. That division allows the partner to assess the feature without replacing its core payment infrastructure.

The implementation currently includes a reusable React module, backend APIs and an Android demonstration app. The APK demonstrates the mobile experience. A production deployment would still require work on authentication, permissions, wallet events, operational controls and the host app's design.

Commercially, this is a software and integration offering. Customer discovery would happen within the partner's existing app experience, supported by its merchant relationships. Adoption still has to be earned through usefulness, but customers would not need to establish another wallet relationship to try the feature.

## 11. A neighbourhood pilot inside one wallet (8:43–9:40)

The proposed next step is a limited pilot with one wallet partner, one neighbourhood and a manageable group of merchants.

A narrow launch is important because local information needs sufficient coverage to be useful. Before inviting customers, the pilot would establish a base of clearly attributed essentials prices and recruit contributors who can keep reports current. The partner could introduce the feature at relevant shopping or budgeting moments within its app.

Before launch, we would agree on what would justify expansion: report quality, repeat useful visits, customer buffer outcomes and campaign economics. We would also define how inaccurate reports and merchant disputes are handled.

I am looking for a wallet partner willing to run that pilot. The offer is to help customers understand their local market, recognise useful community contributions, and make informed emergency-savings decisions within the wallet they already use. We would use the pilot results to decide what to improve and whether to expand.

## 12. Conclusion (9:40–10:00)

Ipon Buffer gives wallet customers useful local information and a clearer savings decision. The next step is a neighbourhood pilot with a wallet partner to test customer value and commercial viability.

## Sources

Sources: https://help.gasbuddy.com/hc/en-us/articles/17437148399511-Reporting-Prices ; https://newsroom.paypal-corp.com/2026-05-11-Venmo-Reimagines-Its-App-Experience . Competitive positioning is a hypothesis, not validated superiority.

Behaviour model: https://www.behaviormodel.org/ . Mechanism is a design hypothesis; no measured behaviour-change claim.