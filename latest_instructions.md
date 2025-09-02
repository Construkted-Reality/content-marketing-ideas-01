lets create a new python script which parses a file containing multiple blog post ideas, and standardizes the formatting so it can be imported into a different script in order to turn the ideas into full blog posts.

Two examples of blog post idea files are @/research/perplexity/cleaned_chats/mobile-lidar_blog_ideas-01Sept2025.md and @/research/perplexity/cleaned_chats/photogrammetry_blog_ideas-02-01Sept2025.md 

You can use them to test the code with.

At the end of each file is a list of URLs. Each url corresponds to the source when the blog idea came from.
I want to move the URL under the corresponding blog post idea. Sometimes there may be multiple URLs for each idea.
Each source has a reference between [ ] brackets. 

the python script should take in a .md or .txt file as input, process it and save the processed result as a new file. 
What is a good format for an standardized output? json? something else?
I will be adding blog post ideas from time to time to this  new file as more ideas get created. Maybe it should be a sqlite database?
it would be nice to track which blog post idea has been turned into an article and which haven't, and it would be nice ti also be able to track other content creation metadata for each idea. Other parameters would be:

| Parameter | Purpose / Why it matters | Example |
|-----------|--------------------------|---------|
| article | the finished article | - |
| voice | Sets the overall stylistic identity (e.g., TheNewYorker) which determines diction, rhythm, and brand perception. | "TheNewYorker" |
| piece_type | Defines the structural format (explainer, listicle, how‑to, etc.) so the model knows how to organise the content. | "explainer" |
| marketing_post_type | Indicates the marketing angle (educational, promotional, thought‑leadership) that shapes messaging focus and CTA style. | "educational" |
| primary_goal | The single objective the article must achieve (educate, convert, inform) to keep the copy purpose‑driven and measurable. | "educate" |
| target_audience | Broad readership definition (enterprise, SMB, developer) guiding language complexity and relevance. | "enterprise" |
| technical_depth | Controls the level of technical detail (low, med, high) to avoid over‑ or under‑explaining for the audience. | "med" |
| title | Concrete headline for SEO and reader capture; the model aligns the narrative to the promised promise. | "Why Data Silos Kill Your AEC Projects" |
| keywords | SEO terms the article must naturally incorporate, improving discoverability. | "data silos, BIM, collaboration, AEC" |
| length | Sets overall word‑count or section count, ensuring the article fits editorial limits and platform constraints. | "1500‑2000 words" |
| sections | Explicit major headings/sub‑headings (e.g., Problem → Causes → Impact → Solutions → Takeaways) giving the model a clear roadmap and improving readability. | "Problem, Causes, Impact, Solutions, Takeaways" |
| call_to_action | The exact action you want the reader to take after reading (download, sign‑up, contact), tying the content back to the marketing funnel. | "Download our free data‑silo checklist" |
| pain_point | Core user problem the article addresses, anchoring the narrative and guaranteeing relevance. | "Teams waste weeks reconciling fragmented 3‑D data across silos" |

These parameters would be filled in over time by other scripts as work is done on the article.
For some of the parameters we would only have a few options to select from . For example Voice would only get 3 options (New Yorker, The Atlantic and Wired) Metadata and specifics for each voice would be listed in a separate table.
Martketing post type would likewise get a set of hardcoded options like :
   - Educational (TOFU): For awareness and education - focus on answering general questions, providing foundational knowledge
   - Comparison (MOFU): For consideration and evaluation - highlight benefits vs competitors, feature comparisons  
   - Conversion-focused (BOFU): For decision-making and purchase - drive action, emphasize value and ROI
   - Case Study: For trust-building at any stage - showcase real-world results and success stories
   - Product Update: For awareness and conversion (TOFU/BOFU) - announce new features, improvements
   - Standards/Policy Analysis: For thought leadership (TOFU) - industry insights, regulatory analysis
   - News Reaction: For engagement (TOFU) - commentary on industry trends and developments

Piece type would also only have a limited set of options to choose from :
explainer, tutorial, methods deep dive, case study, product update, standards/policy analysis, news reaction.

Primary goal would also have a lilmited selection of options:
educate, persuade, announce, compare, troubleshoot

target audience would also have a limited range of options:
enterprise, public sector, academic, hobbyist

Technical depth should have 3 options of low, med, high

Even though we are only setting up limited options now, the system we set up should allow for each to be extended and more options added or each option to have metadata associated with it.

Tell me your suggestions on how to accomplish this




---
 Parameter | Purpose / Why it matters | Example |
|-----------|---------------------------|---------|
| voice | Broad stylistic voice (e.g., TheNewYorker) | "TheNewYorker" |
| tone | Fine‑grained style beyond voice (authoritative, conversational, etc.) | "authoritative yet conversational" |
| piece_type | Type of content (explainer, listicle, how‑to, etc.) | "explainer" |
| marketing_post_type | Marketing angle (educational, promotional, thought‑leadership) | "educational" |
| primary_goal | Core objective (educate, convert, inform) | "educate" |
| target_audience | Who the article is for | "enterprise" |
| audience_persona | Short persona to tailor language | "mid‑level project manager, 5‑10 years experience" |
| technical_depth | Level of technical detail (low, med, high) | "med" |
| title | Concrete headline – also aids SEO | "Why Data Silos Kill Your AEC Projects" |
| slug | URL‑friendly identifier | "data-silos-ace-projects" |
| length | Desired word count or section count | "1500‑2000 words" |
| keywords | SEO keywords to weave in | "data silos, BIM, collaboration, AEC" |
| sections | Explicit major headings/sub‑headings | "Problem, Causes, Impact, Solutions, Takeaways" |
| format | Structural layout (intro‑body‑conclusion, listicle, etc.) | "intro, 5‑point list, summary" |
| call_to_action | Desired reader action after reading | "Download our free data‑silo checklist" |
| brand_guidelines | Brand‑specific language rules | "use ‘construction tech’ instead of ‘building tech’" |
| target_platform | Publication venue (blog, LinkedIn, newsletter) | "company blog" |
| references | Types of sources to cite | "include 2 industry reports and 1 case study" |
| compliance | Legal / regulatory constraints | "no personal data, cite sources" |
| publish_date | When the post should go live | "2025‑09‑15" |
| image_prompt | Description for a featured image or illustration | "render of fragmented 3‑D models representing silos" |
| revision_notes | Guidance for future edits | "leave placeholders for stats to be updated quarterly" |
| justification | Explanation of why each choice was made | Your own rationale |
| pain_point | Summary of the main user pain point | Your own summary |


Refined list
| Parameter | Purpose / Why it matters | Example |
|-----------|--------------------------|---------|
| voice | Sets the overall stylistic identity (e.g., TheNewYorker) which determines diction, rhythm, and brand perception. | "TheNewYorker" |
| piece_type | Defines the structural format (explainer, listicle, how‑to, etc.) so the model knows how to organise the content. | "explainer" |
| marketing_post_type | Indicates the marketing angle (educational, promotional, thought‑leadership) that shapes messaging focus and CTA style. | "educational" |
| primary_goal | The single objective the article must achieve (educate, convert, inform) to keep the copy purpose‑driven and measurable. | "educate" |
| target_audience | Broad readership definition (enterprise, SMB, developer) guiding language complexity and relevance. | "enterprise" |
| technical_depth | Controls the level of technical detail (low, med, high) to avoid over‑ or under‑explaining for the audience. | "med" |
| title | Concrete headline for SEO and reader capture; the model aligns the narrative to the promised promise. | "Why Data Silos Kill Your AEC Projects" |
| keywords | SEO terms the article must naturally incorporate, improving discoverability. | "data silos, BIM, collaboration, AEC" |
| length | Sets overall word‑count or section count, ensuring the article fits editorial limits and platform constraints. | "1500‑2000 words" |
| sections | Explicit major headings/sub‑headings (e.g., Problem → Causes → Impact → Solutions → Takeaways) giving the model a clear roadmap and improving readability. | "Problem, Causes, Impact, Solutions, Takeaways" |
| call_to_action | The exact action you want the reader to take after reading (download, sign‑up, contact), tying the content back to the marketing funnel. | "Download our free data‑silo checklist" |
| pain_point | Core user problem the article addresses, anchoring the narrative and guaranteeing relevance. | "Teams waste weeks reconciling fragmented 3‑D data across silos" |
