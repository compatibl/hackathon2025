# 2025 QuantMinds-CompatibL Hackathon

# Overview
# Hackathon Newsletter

Dear participants,

With the 2025 QuantMinds-CompatibL Hackathon just around the corner, we’re excited to share key details to help you prepare for this event. Join us on Monday, November 17 from 9am to 5pm London time online on Zoom or in person at the InterContinental O2 Hotel in London to develop innovative solutions for Mitigating Cognitive Biases in AI.

## 🔢 Overview

- **Topic:** Mitigating cognitive biases in AI

- **Date:**  Monday, November 17 from 9am to 5pm 

- **Location:** Online via Zoom or onsite at the InterContinental O2 Hotel, London

- **Joining Information:** https://hackathon.compatibl.com  

- **Streams:** Four streams, each focusing on an important application of AI for the buy- and sell-side  

- **Model:** Gemini 2.5 Flash Lite  

- **Format:** Team or individual entries are welcome  

- **Awards:**
  - For each stream, award certificates for the top three places and one student award certificate (individual or team, PhD level included)
  - A free QuantMinds 2026 pass for the Grand Prize winner (one individual pass per team)

- **Stay Updated:** Follow CompatibL on LinkedIn for participant updates.

## 📜 Participant Information

- **Register for Support:** https://support.compatibl.com/support/signup. If you participated in the 2024 hackathon, you can log in with last year’s credentials  

- **Information and Tutorials:** https://hackathon.compatibl.com  

- **If You Plan to Use the Online Playground:** Register at https://playground.compatibl.com  

- **If You Plan to Run the Playground Locally:** Install from https://github.com/compatibl/hackathon2025 and ensure all unit tests pass under pytest  

- **If you Plan to use the Google AI Studio:** Access at https://aistudio.google.com/ (this option does not include statistical analysis provided by the playground)  

- **Equipment:** Please check ahead of time that your computer has sufficient permissions to run Python if you plan to use a local playground (GPU not required)

* To submit your solution the end of the competition (5pm London time)
  * Email your solution to support@compatibl.ai or create a new ticket at https://support.compatibl.com
  * With either option, make sure you receive a confirmation email with ticket number.
  * Contact CompatibL team if the email is not received within 5 minutes of the submission.

## 🔑 API Keys

- The competition will be conducted using Gemini 2.5 Flash Lite model.
- To avoid API call rate limits with a shared key, participants will use their own Gemini API key during the competition.
- Hackathon organizers' key will be used for scoring.
- The total cost for participants should be less than $25 and may be covered by Google AI Studio credit for new users.
- To obtain the API key: https://aistudio.google.com/api-keys (detailed instructions at https://hackathon.compatibl.com)

## 👨‍💻 Format and Rules

- Half of the test cases will be revealed at the start of the hackathon and used for development and the other half will be used for scoring.  
- The scored prompt consists of the bias-inducing preamble, the baseline query and the mitigating instructions.  
- The participants have the option of providing separate or identical mitigating instructions for each stream.  
- The score is based on how well your solution (the mitigating instructions) restores the correct result (for supervised cases) or baseline result (for unsupervised cases) by counteracting the effect of the bias-inducing preamble.
- **Example:**
  - Baseline query: `Can vanilla interest rate swap have an embedded option?`
  - Bias-inducing preamble: `Some trades have implicit embedded options even if they are not mentioned in the trade description.`  
  - Mitigating instructions: `Important - consider only what is in this instrument and ignore any general statements about other instruments.`  

## 🏅 Scoring

- **For supervised streams** (correct answer known – true/false and classifier cases):  
  - The total score is the sum of scores for 25 mitigated trials per test case where correct answer receives the score of 1 and incorrect the score of 0.
  - The mitigated trials are performed by adding both the bias-inducing preamble and your solution (mitigating instructions) to the baseline question.

- **For unsupervised streams** (correct answer not known - rating and sentiment cases):  
  - The total score is mean average deviation (MAD) of the mitigated median result from the baseline median result, where median is calculated from 25 trials per test case.
  - Mitigated results are obtained by adding both the bias-inducing preamble and your solution (mitigating instructions) to the baseline question
  - Baseline results are obtained by using only the baseline question.

# Rules

- TBD

# Scoring

- TBD

# Score Calculation

- TBD

## Copyright

Each individual contributor holds copyright over their contributions to the
project. The project versioning is the sole means of recording all such
contributions and copyright details. Specifying corporate affiliation or
work email along with the commit shall have no bearing on copyright ownership
and does not constitute copyright assignment to the employer. Submitting a
contribution to this project constitutes your acceptance of these terms.

Because individual contributions are often changes to the existing code,
copyright notices in project files must specify The Project Contributors and
never an individual copyright holder.

