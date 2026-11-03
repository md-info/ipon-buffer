# Ipon Buffer: presentation script

November 4, 2026
Allow roughly one minute per slide. Rehearse with a timer; leave room for pauses and showing the app.

## 1. Mika knows her budget. She does not know local prices. (0:00–1:00)

Imagine you're Mika. You've got two thousand pesos in your wallet, you need groceries, and you're trying to put something aside for emergencies.

You know what you need to buy. What you don't know is whether the shop down the street charges less than the one you normally visit. You could walk around and check, but that takes time. If you need transport, it costs money too.

Then there's another decision: after you've covered your expenses, how much can you actually save?

Mika is a fictional example, but those are the two problems I built Ipon Buffer around. Finding affordable essentials nearby, and working out a sensible amount to put into an emergency fund.

## 2. Ipon Buffer (1:00–2:00)

Ipon Buffer brings local price sharing and emergency savings into the e-wallet people already use.

Someone finds affordable rice at a nearby store. They post the price and a photo. Other shoppers can check it, confirm it, and use that information before heading out. Alongside that feed, the app helps each person work out a savings contribution based on their own expenses.

For a wallet company, this adds something useful to an app customers already have. It gives people a reason to open their wallet before they buy, and gives local merchants another way to reach them.

That's the proposal I developed for the ASEAN Financial Health Challenge: help people make everyday spending decisions that leave more room for emergencies.

## 3. One screen connects discovery and saving (2:00–3:00)

Let me walk through what Mika would actually do.

She opens the app. Her emergency buffer sits at the top, with local price posts underneath. Each post shows the product, price, pack size and store, so she can compare the same quantity rather than just picking the lowest number.

She taps a post to see more. If she visits that store and finds the same price, she can confirm it. If she finds something useful herself, she can share a photo and help someone else.

When she's ready to save, she reviews her expenses and sees a suggested deposit. She confirms it once, and the app shows the completed deposit. The demo uses synthetic money. A post or a like never moves money on her behalf.

## 4. AI helps explain expenses (3:00–4:00)

The AI helps with the part people often find tedious: filling in a financial plan.

Mika can describe an upcoming expense in her own words. For example, she might say she has a school payment coming up. The AI turns that description into suggested details for her to check. If something is missing or wrong, she can correct it before saving.

The savings calculation runs separately, using rules that account for her planned essentials. Mika still approves the deposit herself.

The current demo runs the model locally on the computer, and the manual form remains available. The point of the AI is to make planning less work, while leaving the customer in control of what goes into the plan.

## 5. A focused combination (4:00–5:00)

There are familiar ideas here. GasBuddy lets people report fuel prices. Venmo has social recommendations and cashback. Those products show that people already use community information to help decide where to spend.

Ipon Buffer applies that idea to local essentials and puts it beside an emergency-savings plan.

The Venmo comparison is one way to explain the difference: Venmo makes payments social. Ipon Buffer makes local price knowledge social, and connects it to emergency savings.

What matters is whether that connection helps someone like Mika. Can she find useful prices? Does she come back? Does she end up with a stronger buffer? Those are questions for a pilot. The prototype gives us something concrete to test.

## 6. A useful action earns a social response (5:00–6:00)

People need a reason to contribute, too.

Suppose Mika shares a good price. Someone thanks her, and another person visits the shop and confirms it. She can see that her post helped. She earns contribution points, and her name stays attached to the finding.

That gives her some of the satisfaction of posting on social media, with a useful result for her neighbours.

The behaviour model behind this is straightforward. She has a reason to act, the action takes little effort, and the opportunity appears while she's already shopping or using her wallet. That's the motivation, ability and prompt described by BJ Fogg.

I'd test whether those responses encourage accurate contributions. A thank-you and a price confirmation serve different purposes, so the app keeps them separate.

## 7. Revenue fits the wallet’s existing business (6:00–7:00)

How could this make money?

The first option is to sell the software and integration service to a wallet company. The second is to charge for merchant campaigns.

A small grocery might fund cashback on a qualifying purchase. The customer gets an offer on something they need, the merchant gets a chance to win that purchase, and the wallet can charge a campaign fee. The demo already simulates the purchase and cashback flow, including the customer's choice to move cashback into their buffer.

The fee still has to cover the cost of running the service, including support and checking for abuse. Savings or investment referrals could come later through a suitable partner product. Interest on wallet balances isn't revenue we can simply assume belongs to Ipon Buffer.

## 8. The partner buys measurable outcomes (7:00–8:00)

If I were presenting this to a wallet operator, I'd expect them to ask what they get for the cost.

I'd look at whether customers return to check prices, whether merchant offers bring additional purchases, and whether people keep more money in their emergency buffers after withdrawals.

Likes alone wouldn't answer those questions. Neither would counting every purchase made by someone who happened to see an offer. We'd need a comparison to understand what the feature actually changed.

That's why I'd start with a pilot and agree on the measures with the partner. We could compare participating customers with a suitable control group, then look at the benefit alongside campaign spending and operating costs. That would give the company a basis for deciding whether to expand.

## 9. A feature on top of the wallet (8:00–9:00)

This is meant to become a feature within an existing wallet, such as GCash or Maya. Neither company is a partner today.

The wallet would keep its customer accounts, balances, payment approvals and merchant settlement. Ipon Buffer would add the price-sharing experience and savings guidance on top of that structure.

I've built a reusable React module, backend APIs and an Android demo. The APK lets us try the experience on a phone. A company would still need integration work to connect the feature to its own accounts and payment systems.

The advantage is that we can build around a business that already has users and merchants. Customers could discover the feature in the wallet they use, without being asked to join another payment service.

## 10. A neighbourhood pilot inside one wallet (9:00–10:00)

I'd start in one neighbourhood with a small group of merchants and shoppers.

Before inviting more people, we'd make sure there are useful prices to find. An empty feed gives nobody a reason to return. The first contributors would help build that coverage, and merchants could introduce the feature to customers who already use the partner wallet.

Then we'd watch what happens. Are reports staying accurate? Are people using them? Do customers return, and do their buffers grow? Can merchant campaigns cover their costs?

Those answers would tell us what to improve before expanding.

What I'm looking for is a wallet partner willing to test this in one community. Ipon Buffer gives customers a way to learn from nearby shoppers, help each other spend wisely, and choose what they can put aside for the next emergency.

## Sources

Sources: https://help.gasbuddy.com/hc/en-us/articles/17437148399511-Reporting-Prices ; https://newsroom.paypal-corp.com/2026-05-11-Venmo-Reimagines-Its-App-Experience . Competitive positioning is a hypothesis, not validated superiority.

Behaviour model: https://www.behaviormodel.org/ . Mechanism is a design hypothesis; no measured behaviour-change claim.