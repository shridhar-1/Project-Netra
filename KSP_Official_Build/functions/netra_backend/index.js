'use strict';
const express = require('express');
const catalyst = require('zcatalyst-sdk-node');

const app = express();
app.use(express.json());

// ---------------------------------------------------------
// 🧠 THE AGENTIC BRAIN: V5 Bulletproof Extractor
// ---------------------------------------------------------
function extractSearchKeywords(question) {
    const customFillerWords = [
        'what', 'where', 'who', 'how', 'when', 'why', 'did', 'happen', 'occur', 'take', 'place',
        'is', 'the', 'in', 'near', 'at', 'yar', 'madidddu', 'hatra', 'ide', 'tell', 'me', 'about',
        'case', 'cases', 'any', 'details', 'of', 'a', 'an', 'and', 'or', 'for', 'to', 'on', 'with', 'was',
        'recent', 'recently', 'some', 'these'
    ];

    let text = question.toLowerCase();

    text = text.replace(/ಕೊಲೆ|kole/g, 'murder');
    text = text.replace(/ಕಳ್ಳತನ|kallatana/g, 'theft');
    text = text.replace(/ದರೋಡೆ|darode/g, 'robbery');
    text = text.replace(/ವಂಚನೆ|vanchane/g, 'fraud');
    text = text.replace(/ಅಪಹರಣ|apaharana/g, 'kidnapping');

    text = text.replace(/murders/g, 'murder');
    text = text.replace(/thefts/g, 'theft');
    text = text.replace(/robberies/g, 'robbery');

    text = text.replace(/busstand/g, 'bus stand');
    text = text.replace(/collegeroad/g, 'college road');
    text = text.replace(/templestreet/g, 'temple street');
    text = text.replace(/murdeswar/g, 'murdeshwar');

    const cleanText = text.replace(/[^\p{L}\p{N}\s]/gu, '');
    const words = cleanText.split(/\s+/);

    return words.filter(w => !customFillerWords.includes(w) && w.length > 2);
}

app.post('/chat', async (req, res) => {
    try {
        const originalUserPrompt = req.body?.message || req.body?.question || "Can you summarize these recent cases?";
        const targetLanguage = req.body.language || 'kannada';

        // ---------------------------------------------------------
        // 🛡️ GEOGRAPHICAL SECURITY FILTER
        // ---------------------------------------------------------
        const userRole = req.body.userRole || 'State_HQ';

        let jurisdictionFilter = "";

        if (userRole === 'District_SP') {
            jurisdictionFilter = " AND District = 'Uttara Kannada'";
        } else if (userRole === 'Taluk_PSI') {
            jurisdictionFilter = " AND Taluk = 'Honnavar'";
        }
        // Note: 'State_HQ' gets no filter — full database access

        console.log(`\n🗣️ Original Input: ${originalUserPrompt} (${targetLanguage}) [Role: ${userRole}]`);

        let searchPrompt = originalUserPrompt;

        if (targetLanguage === 'kannada' || targetLanguage === 'kanglish') {
            try {
                const transRes = await fetch(
                    `https://api.mymemory.translated.net/get?q=${encodeURIComponent(originalUserPrompt)}&langpair=kn|en`
                );
                const transData = await transRes.json();

                if (transData.responseData && transData.responseData.translatedText) {
                    searchPrompt = transData.responseData.translatedText;
                    console.log(`🔄 Translated for DB Search: ${searchPrompt}`);
                }
            } catch (error) {
                console.log("Translation Layer Failed, using original prompt.");
            }
        }

        delete req.headers.cookie;
        delete req.headers.authorization;

        const catalystApp = catalyst.initialize(req);
        const zcql = catalystApp.zcql();

        const searchWords = extractSearchKeywords(searchPrompt);

        // Base query with jurisdiction filter injected
        let caseQuery = jurisdictionFilter
            ? `SELECT * FROM casemasters WHERE 1=1${jurisdictionFilter} LIMIT 5`
            : `SELECT * FROM casemasters LIMIT 5`;

        let caseResults = [];

        if (searchWords.length > 0) {
            const escapeSQL = (str) => str.replace(/'/g, "''");
            const safeWords = searchWords.map(word => escapeSQL(word));

            const buildOrClause = (column) => {
                return safeWords.map(word => {
                    const lower = word.toLowerCase();
                    const cap   = word.charAt(0).toUpperCase() + word.slice(1);
                    const upper = word.toUpperCase();
                    return `(${column} LIKE '%${lower}%' OR ${column} LIKE '%${cap}%' OR ${column} LIKE '%${upper}%')`;
                }).join(' OR ');
            };

            const crimeClause = buildOrClause('CrimeGroupName');
            const catClause   = buildOrClause('LookupValue');
            const distClause  = buildOrClause('DistrictName');

            let crimeHeadIds    = [];
            let categoryIds     = [];
            let districtUnitIds = [];

            console.log(`\n🤖 Agentic AI executing parallel multi-table scan...`);

            const [headRes, catRes, distRes] = await Promise.all([
                zcql.executeZCQLQuery(`SELECT * FROM CrimeHead WHERE ${crimeClause}`).catch(e => {
                    console.log("⚠️ CrimeHead lookup failed:", e.message || e);
                    return [];
                }),
                zcql.executeZCQLQuery(`SELECT * FROM CaseCategory WHERE ${catClause}`).catch(e => {
                    console.log("⚠️ CaseCategory lookup failed:", e.message || e);
                    return [];
                }),
                zcql.executeZCQLQuery(`SELECT * FROM District WHERE ${distClause}`).catch(e => {
                    console.log("⚠️ District lookup failed:", e.message || e);
                    return [];
                })
            ]);

            if (headRes.length) headRes.forEach(row => crimeHeadIds.push(Number(row.CrimeHead.CrimeHeadID)));
            if (catRes.length)  catRes.forEach(row  => categoryIds.push(Number(row.CaseCategory.CaseCategoryID)));

            if (distRes.length) {
                const dIds = distRes.map(row => Number(row.District.DistrictID));
                const unitClause = dIds.map(id => `DistrictID = ${id}`).join(' OR ');
                const unitRes = await zcql.executeZCQLQuery(
                    `SELECT * FROM Unit WHERE ${unitClause}`
                ).catch(e => {
                    console.log("⚠️ Unit lookup failed:", e.message || e);
                    return [];
                });
                unitRes.forEach(u => districtUnitIds.push(Number(u.Unit.UnitID)));
            }

            let conditions = [];
            if (crimeHeadIds.length > 0) {
                conditions.push(`CrimeMajorHeadID IN (${[...new Set(crimeHeadIds)].join(',')})`);
            }
            if (categoryIds.length > 0) {
                conditions.push(`CaseCategoryID IN (${[...new Set(categoryIds)].join(',')})`);
            }
            if (districtUnitIds.length > 0) {
                conditions.push(`PoliceStationID IN (${[...new Set(districtUnitIds)].join(',')})`);
            }

            if (conditions.length > 0) {
                // ✅ PATH 1: Reverse lookup matched — run precise structured query
                caseQuery = `SELECT * FROM casemasters WHERE ${conditions.join(' AND ')}${jurisdictionFilter} LIMIT 5`;

                console.log(`[SECURITY LOG] Executing Query as ${userRole}:`, caseQuery);
                console.log(`🎯 Reverse Lookup Match! Executing: ${caseQuery}`);
                caseResults = await zcql.executeZCQLQuery(caseQuery);

            } else {
                // ✅ PATH 2: No exact tables matched — Titanium Paginated Deep Scan
                console.log(`⚠️ No exact tables matched. Initiating Table-by-Table Deep Scan...`);

                // 🛡️ THE TITANIUM FIX: TABLE-BY-TABLE PAGINATION
                caseResults = [];
                let offset       = 0;
                const limit      = 300;  // Zoho's maximum allowed rows per chunk
                let keepScanning = true;
                const maxPages   = 20;   // Scans up to 6,000 rows (20 pages × 300). Increase if needed!

                console.log(`[SECURITY LOG] Deep Scan started for ${userRole}...`);

                while (keepScanning && offset < (maxPages * limit)) {

                    // Build the paginated query — "turn the page" with OFFSET
                    let pageQuery = jurisdictionFilter
                        ? `SELECT * FROM casemasters WHERE 1=1${jurisdictionFilter} LIMIT ${limit} OFFSET ${offset}`
                        : `SELECT * FROM casemasters LIMIT ${limit} OFFSET ${offset}`;

                    const rawCases = await zcql.executeZCQLQuery(pageQuery).catch(e => {
                        console.log("⚠️ Pagination query failed:", e.message || e);
                        return [];
                    });

                    // If we get 0 rows back, we've reached the very end of the database!
                    if (!rawCases || rawCases.length === 0) {
                        console.log(`🔚 Reached the end of the database at offset ${offset}.`);
                        break;
                    }

                    // ⚡ THE "EARLY EXIT" HACKER LOOP FOR THIS SPECIFIC PAGE
                    for (const row of rawCases) {
                        const facts    = (row.casemasters.BriefFacts || "").toLowerCase();
                        const hasMatch = searchWords.some(word => facts.includes(word.toLowerCase()));

                        if (hasMatch) {
                            caseResults.push(row);
                        }

                        // Stop the EXACT millisecond we find 5 total cases across all pages!
                        if (caseResults.length === 5) {
                            console.log(`⚡ BOOM! Found 5 cases early at offset ${offset}. Aborting deep scan!`);
                            keepScanning = false;
                            break;
                        }
                    }

                    // Move to the next "page" of 300 rows
                    offset += limit;
                }
            }

        } else {
            // ✅ PATH 3: No search keywords — return generic recent cases
            caseQuery = caseQuery.replace(/;/g, '');
            console.log(`[SECURITY LOG] Executing Query as ${userRole}:`, caseQuery);
            caseResults = await zcql.executeZCQLQuery(caseQuery);
        }

        console.log(`✅ Final Data Pipeline returned ${caseResults.length} matching rows!\n`);

        // ---------------------------------------------------------
        // 🛡️ GUARD CLAUSE: No records found
        // ---------------------------------------------------------
        if (!caseResults || caseResults.length === 0) {
            console.log("🛡️ Guard Clause Triggered: No records found. Skipping LLM call.");

            let guardAnswer = "I'm sorry, I couldn't find any matching case files in the database for those keywords.";

            if (targetLanguage === 'kannada' || targetLanguage === 'kanglish') {
                try {
                    const backTransRes = await fetch(
                        `https://api.mymemory.translated.net/get?q=${encodeURIComponent(guardAnswer)}&langpair=en|kn`
                    );
                    const backTransData = await backTransRes.json();
                    if (backTransData.responseData && backTransData.responseData.translatedText) {
                        guardAnswer = backTransData.responseData.translatedText;
                    }
                } catch (e) {}
            }

            return res.status(200).json({
                status: 'success',
                answer: guardAnswer,
                ai_answer: guardAnswer,
                prompt_preview: `Agentic Search Triggered on Keywords: [${searchWords.join(', ') || 'None'}]`
            });
        }

        // ---------------------------------------------------------
        // 🔗 JOIN: Fetch related Accused, Victim, Complaint data
        // ---------------------------------------------------------
        const caseIdsArray  = caseResults.map(c => c.casemasters.CaseMasterID);
        const caseIdsString = caseIdsArray.join(',');

        let accusedResults   = [];
        let victimResults    = [];
        let complaintResults = [];

        if (caseIdsArray.length > 0) {
            accusedResults = await zcql.executeZCQLQuery(
                `SELECT * FROM Accused WHERE CaseMasterID IN (${caseIdsString})`
            );

            try {
                victimResults = await zcql.executeZCQLQuery(
                    `SELECT * FROM Victim WHERE CaseMasterID IN (${caseIdsString})`
                );
                complaintResults = await zcql.executeZCQLQuery(
                    `SELECT * FROM ComplaintDetails WHERE CaseMasterID IN (${caseIdsString})`
                );
            } catch (e) {
                console.log("⚠️ Minor warning: Victim or ComplaintDetails tables might not exist yet.");
            }
        }

        // ---------------------------------------------------------
        // 📋 BUILD CONTEXT STRING FOR LLM
        // ---------------------------------------------------------
        let caseContext = "Here is the database of cases:\n";
        caseResults.forEach((caseItem, index) => {
            const caseData = caseItem.casemasters;
            const caseId   = Number(caseData.CaseMasterID);
            const safeCrimeNo = caseData.CrimeNo
                ? Number(caseData.CrimeNo).toLocaleString('fullwide', { useGrouping: false })
                : 'Unknown';

            const matchingAccused = accusedResults
                .filter(a => Number(a.Accused.CaseMasterID) === caseId)
                .map(a => a.Accused.AccusedName)
                .join(", ");

            const matchingVictims = victimResults
                .filter(v => Number(v.Victim.CaseMasterID) === caseId)
                .map(v => v.Victim.VictimName)
                .join(", ");

            const matchingComplainants = complaintResults
                .filter(c => Number(c.ComplaintDetails.CaseMasterID) === caseId)
                .map(c => c.ComplaintDetails.ComplainantName)
                .join(", ");

            const fullFacts  = caseData.BriefFacts || "";
            const shortFacts = fullFacts.length > 300
                ? fullFacts.substring(0, 300) + "..."
                : fullFacts;

            caseContext += `Case ${index + 1}: Crime No ${safeCrimeNo}. Accused: ${matchingAccused || 'Unknown'}. Victim(s): ${matchingVictims || 'None'}. Complainant(s): ${matchingComplainants || 'None'}. Details: ${shortFacts}\n---\n`;
        });

        // ---------------------------------------------------------
        // 🧠 THE "NO-NONSENSE MACHINE" PROMPT (Fixes AI Translating Labels)
        // ---------------------------------------------------------
        const systemPrompt = `You are a rigid data-extraction and translation machine.
You will receive a list of police database records.

Task 1: Extract the real names of the accused ONLY from the provided database records.
Task 2: Write a very short, 1-sentence summary of the crimes.
Task 3: Translate the names and the summary ENTIRELY into ${targetLanguage.toUpperCase()}.

CRITICAL RULES:
- NEVER TRANSLATE THE LABELS! The labels must strictly remain "**Accused:**" and "**Case Details:**" in English.
- Put the names on the Accused line, and the summary on the Case Details line.
- NO internal monologue or thinking out loud.
- NO English explanations or translations in parentheses.
- Output ONLY the final text block below.

|||FINAL_SUMMARY|||
**Accused:** [Insert Real Translated Names Here]
**Case Details:** [Insert 1-Sentence Translated Summary Here]`;

        const userPrompt = `DATABASE RECORDS:
${caseContext}

USER QUESTION: ${searchPrompt}

API RESPONSE (Start exactly with |||FINAL_SUMMARY|||):`;

        // ---------------------------------------------------------
        // 🔑 ZOHO AUTH TOKEN
        // ---------------------------------------------------------
        const projectId    = "46199000000013024";
        const orgId        = "60075406816";
        const clientId     = "1000.VJZ9TW78N46U3UJ14A4TIG0XU4S3KR";
        const clientSecret = "ec741df8674e3e71e32c8171e3ae431aa29372c436";
        const refreshToken = "1000.7b345732ebd6d2dafc2f3fae0a4c00fc.3739ade545fb3dbb765d217223c4daa0";

        const tokenUrl = `https://accounts.zoho.in/oauth/v2/token?refresh_token=${refreshToken}&client_id=${clientId}&client_secret=${clientSecret}&grant_type=refresh_token`;
        const tokenResponse = await fetch(tokenUrl, { method: 'POST' });
        const tokenData     = await tokenResponse.json();

        if (!tokenData.access_token) {
            throw new Error("Zoho Auth Server did not return an access token.");
        }

        const authToken = `Zoho-oauthtoken ${tokenData.access_token}`;
        const llmUrl    = `https://api.catalyst.zoho.in/quickml/v1/project/${projectId}/glm/chat`;

        const requestBody = {
            model: "crm-di-glm47b_30b_it",
            messages: [
                { role: "system", content: systemPrompt },
                { role: "user",   content: userPrompt }
            ],
            max_tokens:  2048,
            temperature: 0.1,
            stream:      false
        };

        const response = await fetch(llmUrl, {
            method: 'POST',
            headers: {
                'Content-Type':  'application/json',
                'CATALYST-ORG':  orgId,
                'Authorization': authToken
            },
            body: JSON.stringify(requestBody)
        });

        const aiData = await response.json();

        // ---------------------------------------------------------
        // 🚨 LLM ERROR HANDLER
        // ---------------------------------------------------------
        if (aiData.code === "INTERNAL_SERVER_ERROR" || aiData.error) {
            console.log("🚨 ZOHO API ERROR RAW DETAILS:", JSON.stringify(aiData, null, 2));

            let errorAnswer = "I found the cases in the database, but my language processor is overloaded. Please try asking again in a moment.";

            if (targetLanguage === 'kannada' || targetLanguage === 'kanglish') {
                try {
                    const backTransRes = await fetch(
                        `https://api.mymemory.translated.net/get?q=${encodeURIComponent(errorAnswer)}&langpair=en|kn`
                    );
                    const backTransData = await backTransRes.json();
                    if (backTransData.responseData && backTransData.responseData.translatedText) {
                        errorAnswer = backTransData.responseData.translatedText;
                    }
                } catch (e) {}
            }

            return res.status(200).json({
                status: 'success',
                answer: errorAnswer,
                ai_answer: errorAnswer
            });
        }

        // ---------------------------------------------------------
        // 🎯 V8 "ISOLATION ROOM" EXTRACTOR
        // ---------------------------------------------------------
        let rawAnswer = aiData.choices?.[0]?.message?.content || aiData.response || aiData.output || "";

        let finalAccused = "Unknown";
        let finalDetails = "Could not generate summary.";

        // Grab ONLY the bottom section — ignore all AI thought-process above it
        let cleanBlock = rawAnswer;
        if (rawAnswer.includes("|||FINAL_SUMMARY|||")) {
            cleanBlock = rawAnswer.split("|||FINAL_SUMMARY|||").pop();
        } else if (rawAnswer.lastIndexOf("**Accused:**") !== -1) {
            cleanBlock = rawAnswer.substring(rawAnswer.lastIndexOf("**Accused:**"));
        }

        // Extract Accused
        const accusedMatch = cleanBlock.match(
            /(?:\*\*Accused:\*\*|Accused:|\*\*ಆರೋಪಿಗಳು:\*\*|ಆರೋಪಿಗಳು:)\s*([^\n]+)/i
        );
        if (accusedMatch) {
            let tempAccused = accusedMatch[1].replace(/\*\*/g, '').replace(/`/g, '').trim();
            // Arrow Sniper: If AI writes "Template -> Actual Names", grab only the names!
            finalAccused = tempAccused.includes("->") ? tempAccused.split("->").pop().trim() : tempAccused;
        }

        // Extract Case Details
        const detailsMatch = cleanBlock.match(
            /(?:\*\*Case Details:\*\*|Case Details:|\*\*ಪ್ರಕರಣದ ವಿವರಗಳು:\*\*|ಪ್ರಕರಣದ ವಿವರಗಳು:)\s*([\s\S]*?)(?=\n\n|\n\d\.|$)/i
        );
        if (detailsMatch) {
            let tempDetails = detailsMatch[1].replace(/\*\*/g, '').replace(/`/g, '').trim();
            finalDetails = tempDetails.includes("->") ? tempDetails.split("->").pop().trim() : tempDetails;
        }

        // 🛡️ Ultimate Safety Net: if both extractors failed, dump the raw clean block
        if (finalAccused === "Unknown" && finalDetails === "Could not generate summary.") {
            finalDetails = cleanBlock.replace(/\*\*/g, '').trim() || "No data returned from AI.";
        }

        // Rebuild the final clean string manually
        let cleanAnswer = `**Accused:** ${finalAccused}\n**Case Details:** ${finalDetails}`;

        return res.status(200).json({
            status: 'success',
            answer: cleanAnswer,
            ai_answer: cleanAnswer
        });

    } catch (err) {
        console.error("Server Error:", err);
        return res.status(500).json({
            status: 'error',
            error: err.message
        });
    }
});

module.exports = app;