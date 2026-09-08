import axios from 'axios';

export const SUPPORTED_LANGUAGES = [
  { code: 'en', name: 'English', nativeName: 'English', script: 'Latin' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', script: 'Devanagari' },
  { code: 'sa', name: 'Sanskrit', nativeName: 'संस्कृतम्', script: 'Devanagari' },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी', script: 'Devanagari' },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা', script: 'Bengali' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', script: 'Tamil' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', script: 'Telugu' },
  { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ', script: 'Kannada' },
  { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം', script: 'Malayalam' },
  { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી', script: 'Gujarati' },
  { code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ', script: 'Gurmukhi' },
  { code: 'or', name: 'Odia', nativeName: 'ଓଡ଼ିଆ', script: 'Odia' },
];

const BHASHINI_API_URL = import.meta.env.VITE_BHASHINI_API_URL || 'https://api.bhashini.gov.in';
const BHASHINI_API_KEY = import.meta.env.VITE_BHASHINI_API_KEY || '';
const BHASHINI_USER_ID = import.meta.env.VITE_BHASHINI_USER_ID || '';
const BHASHINI_PIPELINE_ID = import.meta.env.VITE_BHASHINI_PIPELINE_ID || '';

// In-memory translation cache (key: `${sourceLang}:${targetLang}:${text}`)
const translationCache = new Map();

// Built-in offline dictionary translations for common UI phrases and quick responses
const OFFLINE_DICTIONARY = {
  'hi': {
    'Hello! I am **AyurPedia**, your specialized AI assistant for Ayurvedic Intellectual Property Rights (IPR), Patent regulations, Traditional Knowledge Digital Library (TKDL) norms, and regulatory frameworks (e.g. FSSAI Ayurveda-Aahar, WIPO GRATK Treaty).\n\nYou can ask a regulatory or legal question directly, or use our **Classification Tool** to categorize your herbal formulation.': 'नमस्ते! मैं **आयुर्पीडिया** हूँ, आयुर्वेद बौद्धिक संपदा अधिकार (IPR), पेटेंट नियम, पारंपरिक ज्ञान डिजिटल लाइब्रेरी (TKDL) मानदंडों और नियामक ढांचे (जैसे FSSAI आयुर्वेद-आहार, WIPO GRATK संधि) के लिए आपका विशेष AI सहायक।\n\nआप सीधे नियामक या कानूनी प्रश्न पूछ सकते हैं, या अपनी औषधीय तैयारी को वर्गीकृत करने के लिए हमारे **वर्गीकरण उपकरण** का उपयोग कर सकते हैं।',
    'Hello! I can help with Ayurveda IPR and regulatory questions. Start by classifying your formulation, or ask a question directly.': 'नमस्ते! मैं आयुर्वेद आईपीआर और नियामक प्रश्नों में आपकी सहायता कर सकता हूँ। अपने योग को वर्गीकृत करके शुरू करें, या सीधे कोई प्रश्न पूछें।',
    'What is Section 3(p)?': 'पेटेंट अधिनियम की धारा 3(p) क्या है?',
    'What are the disclosure requirements under WIPO GRATK?': 'WIPO GRATK के तहत प्रकटीकरण आवश्यकताएं क्या हैं?',
    'How to register Ayurveda Aahar?': 'आयुर्वेद आहार को कैसे पंजीकृत करें?',
    'Classify Formulation': 'योग का वर्गीकरण करें',
    'Verified': 'सत्यापित',
    'High confidence': 'उच्च विश्वसनीयता',
    'Medium confidence': 'मध्यम विश्वसनीयता',
    'Low confidence': 'निम्न विश्वसनीयता',
    'This is information, not legal advice. Consult a qualified legal professional.': 'यह जानकारी है, कानूनी सलाह नहीं। योग्य कानूनी पेशेवर से परामर्श लें।',
    'Contact Legal Facilitator': 'कानूनी विशेषज्ञ से संपर्क करें',
    'India': 'भारत',
    'International': 'अंतर्राष्ट्रीय',
    'Both': 'दोनों',
  },
  'ta': {
    'Hello! I am **AyurPedia**, your specialized AI assistant for Ayurvedic Intellectual Property Rights (IPR), Patent regulations, Traditional Knowledge Digital Library (TKDL) norms, and regulatory frameworks (e.g. FSSAI Ayurveda-Aahar, WIPO GRATK Treaty).\n\nYou can ask a regulatory or legal question directly, or use our **Classification Tool** to categorize your herbal formulation.': 'வணக்கம்! நான் **ஆயுர்பீடியா**, ஆயுர்வேத அறிவுசார் சொத்து உரிமைகள் (IPR), காப்புரிமை ஒழுங்குமுறைகள், பாரம்பரிய அறிவு டிஜிட்டல் நூலகம் (TKDL) விதிமுறைகள் மற்றும் ஒழுங்குமுறை கட்டமைப்புகளுக்கான (எ.கா FSSAI ஆயுர்வேத-ஆஹார், WIPO GRATK ஒப்பந்தம்) உங்கள் சிறப்பு AI உதவியாளர்.\n\nநீங்கள் ஒழுங்குமுறை அல்லது சட்ட கேள்வியை நேரடியாகக் கேட்கலாம், அல்லது உங்கள் மூலிகை தயாரிப்பை வகைப்படுத்த எங்கள் **வகைப்படுத்தல் கருவியை** பயன்படுத்தலாம்.',
    'Classify Formulation': 'தயாரிப்பை வகைப்படுத்து',
    'Verified': 'சரிபார்க்கப்பட்டது',
    'High confidence': 'அதிக நம்பிக்கை',
    'Medium confidence': 'மிதமான நம்பிக்கை',
    'Low confidence': 'குறைந்த நம்பிக்கை',
    'India': 'இந்தியா',
    'International': 'சர்வதேச',
    'Both': 'இரண்டும்',
  },
  'te': {
    'Hello! I am **AyurPedia**, your specialized AI assistant for Ayurvedic Intellectual Property Rights (IPR), Patent regulations, Traditional Knowledge Digital Library (TKDL) norms, and regulatory frameworks (e.g. FSSAI Ayurveda-Aahar, WIPO GRATK Treaty).\n\nYou can ask a regulatory or legal question directly, or use our **Classification Tool** to categorize your herbal formulation.': 'హలో! నేను **ఆయుర్పీడియా**, ఆయుర్వేద మేధస్సు ఆస్తి హక్కులు (IPR), పేటెంట్ నియమాలు, సంప్రదాయ జ్ఞానం డిజిటల్ లైబ్రరీ (TKDL) నియమాలు మరియు నియంత్రణ చట్టాలకు (ఉదా. FSSAI ఆయుర్వేద-ఆహారం, WIPO GRATK ఒప్పందం) మీ ప్రత్యేక AI సహాయకుడిని.\n\nమీరు నియంత్రణ లేదా చట్టపరమైన ప్రశ్నను నేరుగా అడగవచ్చు, లేదా మీ హర్బల్ ఫార్ములేషన్‌ను వర్గీకరించడానికి మా **వర్గీకరణ సాధనాన్ని** ఉపయోగించవచ్చు.',
    'Classify Formulation': 'ఫార్ములేషన్‌ను వర్గీకరించు',
    'Verified': 'ధృవీకరించబడింది',
    'High confidence': 'అధిక విశ్వాసం',
    'Medium confidence': 'మధ్యమ విశ్వాసం',
    'Low confidence': 'తక్కువ విశ్వాసం',
    'India': 'భారతదేశం',
    'International': 'అంతర్జాతీయ',
    'Both': 'రెండూ',
  },
  'bn': {
    'Hello! I am **AyurPedia**, your specialized AI assistant for Ayurvedic Intellectual Property Rights (IPR), Patent regulations, Traditional Knowledge Digital Library (TKDL) norms, and regulatory frameworks (e.g. FSSAI Ayurveda-Aahar, WIPO GRATK Treaty).\n\nYou can ask a regulatory or legal question directly, or use our **Classification Tool** to categorize your herbal formulation.': 'নমস্কার! আমি **আয়ুর্পিডিয়া**, আয়ুর্বেদ বৌদ্ধিক সম্পত্তি অধিকার (IPR), পেটেন্ট প্রবিধান, ঐতিহ্যবাহী জ্ঞান ডিজিটাল লাইব্রেরি (TKDL) নিয়ম এবং নিয়ন্ত্রক কাঠামোর (যেমন FSSAI আয়ুর্বেদ-আহার, WIPO GRATK চুক্তি) জন্য আপনার বিশেষ AI সহকারী।\n\nআপনি সরাসরি নিয়ন্ত্রক বাা আইনি প্রশ্ন জিজ্ঞাসা করতে পারেন, অথবা আপনার ভেষজ ফর্মুলেশন শ্রেণীবদ্ধ করতে আমাদের **শ্রেণীবদ্ধকরণ টুল** ব্যবহার করতে পারেন।',
    'Classify Formulation': 'ফর্মুলেশন শ্রেণীবদ্ধ করুন',
    'Verified': 'যাচাই করা হয়েছে',
    'High confidence': 'উচ্চ আস্থা',
    'Medium confidence': 'মধ্যম আস্থা',
    'Low confidence': 'নিম্ন আস্থা',
    'India': 'ভারত',
    'International': 'আন্তর্জাতিক',
    'Both': 'উভয়',
  },
  'mr': {
    'Hello! I am **AyurPedia**, your specialized AI assistant for Ayurvedic Intellectual Property Rights (IPR), Patent regulations, Traditional Knowledge Digital Library (TKDL) norms, and regulatory frameworks (e.g. FSSAI Ayurveda-Aahar, WIPO GRATK Treaty).\n\nYou can ask a regulatory or legal question directly, or use our **Classification Tool** to categorize your herbal formulation.': 'नमस्कार! मी **आयुर्पीडिया**, आयुर्वेद बौद्धिक संपदा अधिकार (IPR), पेटंट नियम, पारंपरिक ज्ञान डिजिटल लायब्ररी (TKDL) नियम आणि नियामक चौकटींसाठी (उदा. FSSAI आयुर्वेद-आहार, WIPO GRATK तह) तुमचा विशेष AI सहाय्यक आहे.\n\nतुम्ही थेट नियामक किंवा कायदेशीर प्रश्न विचारू शकता, किंवा तुमच्या औषधीय फॉर्म्युलेशनचे वर्गीकरण करण्यासाठी आमच्या **वर्गीकरण साधनाचा** वापर करू शकता.',
    'Classify Formulation': 'फॉर्म्युलेशनचे वर्गीकरण करा',
    'Verified': 'सत्यापित',
    'High confidence': 'उच्च विश्वास',
    'Medium confidence': 'मध्यम विश्वास',
    'Low confidence': 'कमी विश्वास',
    'India': 'भारत',
    'International': 'आंतरराष्ट्रीय',
    'Both': 'दोन्ही',
  },
  'kn': {
    'Hello! I am **AyurPedia**, your specialized AI assistant for Ayurvedic Intellectual Property Rights (IPR), Patent regulations, Traditional Knowledge Digital Library (TKDL) norms, and regulatory frameworks (e.g. FSSAI Ayurveda-Aahar, WIPO GRATK Treaty).\n\nYou can ask a regulatory or legal question directly, or use our **Classification Tool** to categorize your herbal formulation.': 'ನಮಸ್ಕಾರ! ನಾನು **ಆಯುರ್ಪೀಡಿಯಾ**, ಆಯುರ್ವೇದ ಬೌದ್ಧಿಕ ಆಸ್ತಿ ಹಕ್ಕುಗಳು (IPR), ಪೇಟೆಂಟ್ ನಿಯಮಗಳು, ಸಂಪ್ರದಾಯ ಜ್ಞಾನ ಡಿಜಿಟಲ್ ಲೈಬ್ರರಿ (TKDL) ಮಾನದಂಡಗಳು ಮತ್ತು ನಿಯಂತ್ರಕ ಚೌಕಟ್ಟಗಳಿಗಾಗಿ (ಉದಾ. FSSAI ಆಯುರ್ವೇದ-ಆಹಾರ, WIPO GRATK ಒಪ್ಪಂದದ) ನಿಮ್ಮ ವಿಶೇಷ AI ಸಹಾಯಕ.\n\nನೀವು ನೇಯವಾಗಿ ನಿಯಂತ್ರಕ ಅಥವಾ ಕಾನೂನು ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಬಹುದು, ಅಥವಾ ನಿಮ್ಮ ಔಷಧೀಯ ಫಾರ್ಮುಲೇಶನ್ ಅನ್ನು ವರ್ಗೀಕರಿಸಲು ನಮ್ಮ **ವರ್ಗೀಕರಣ ಸಾಧನ**ವನ್ನು ಬಳಸಬಹುದು.',
    'Classify Formulation': 'ಫಾರ್ಮುಲೇಶನ್ ವರ್ಗೀಕರಿಸಿ',
    'Verified': 'ಪರಿಶೀಲಿಸಲಾಗಿದೆ',
    'High confidence': 'ಹೆಚ್ಚಿನ ವಿಶ್ವಾಸ',
    'Medium confidence': 'ಮಧ್ಯಮ ವಿಶ್ವಾಸ',
    'Low confidence': 'ಕಡಿಮೆ ವಿಶ್ವಾಸ',
    'India': 'ಭಾರತ',
    'International': 'ಅಂತರರಾಷ್ಟ್ರೀಯ',
    'Both': 'ಎರಡೂ',
  },
  'ml': {
    'Hello! I am **AyurPedia**, your specialized AI assistant for Ayurvedic Intellectual Property Rights (IPR), Patent regulations, Traditional Knowledge Digital Library (TKDL) norms, and regulatory frameworks (e.g. FSSAI Ayurveda-Aahar, WIPO GRATK Treaty).\n\nYou can ask a regulatory or legal question directly, or use our **Classification Tool** to categorize your herbal formulation.': 'നമസ്കാരം! ഞാൻ **ആയുർപീഡിയ**, ആയുർവേദ ബൗദ്ധിക സ്വത്തവകാശങ്ങൾ (IPR), പേറ്റന്റ് നിയമങ്ങൾ, പാരമ്പര്യ അറിവ് ഡിജിറ്റൽ ലൈബ്രറി (TKDL) മാനദണ്ഡങ്ങൾ, നിയന്ത്രണ ചട്ടക്കൂടുകൾക്കായി (ഉദാ. FSSAI ആയുർവേദ-ആഹാരം, WIPO GRATK ഉടമ്പടം) നിങ്ങളുടെ പ്രത്യേക AI സഹായി.\n\nനിങ്ങൾ നേരിട്ട് നിയന്ത്രണ അല്ലെങ്കിൽ നിയമ ചോദ്യം ചോദിക്കാം, അല്ലെങ്കിൽ നിങ്ങളുടെ ഹെർബൽ ഫോർമുലേഷൻ വർഗ്ഗീകരിക്കാൻ ഞങ്ങളുടെ **വർഗ്ഗീകരണ ടൂൾ** ഉപയോഗിക്കാം.',
    'Classify Formulation': 'ഫോർമുലേഷൻ വർഗ്ഗീകരിക്കുക',
    'Verified': 'പരിശോധിച്ചു',
    'High confidence': 'ഉയർന്ന വിശ്വാസം',
    'Medium confidence': 'ഇടത്തരം വിശ്വാസം',
    'Low confidence': 'കുറഞ്ഞ വിശ്വാസം',
    'India': 'ഇന്ത്യ',
    'International': 'അന്താരാഷ്ട്ര',
    'Both': 'രണ്ടും',
  },
  'gu': {
    'Hello! I am **AyurPedia**, your specialized AI assistant for Ayurvedic Intellectual Property Rights (IPR), Patent regulations, Traditional Knowledge Digital Library (TKDL) norms, and regulatory frameworks (e.g. FSSAI Ayurveda-Aahar, WIPO GRATK Treaty).\n\nYou can ask a regulatory or legal question directly, or use our **Classification Tool** to categorize your herbal formulation.': 'નમસ્તે! હું **આયુર્પીડિયા**, આયુર્વેદ બૌદ્ધિક સંપદા અધિકારો (IPR), પેટન્ટ નિયમો, પરંપરાગત જ્ઞાન ડિજિટલ લાઇબ્રેરી (TKDL) માનદંડો અને નિયામક માળખાઓ માટે (દા. FSSAI આયુર્વેદ-આહાર, WIPO GRATK સંધિ) તમારો વિશેષ AI સહાયક છું.\n\nતમે સીધી જ નિયામક અથવા કાનૂની પ્રશ્ન પૂછી શકો છો, અથવા તમારી હર્બલ ફોર્મ્યુલેશનનું વર્ગીકરણ કરવા મારા **વર્ગીકરણ સાધન**નો ઉપયોગ કરી શકો છો.',
    'Classify Formulation': 'ફોર્મ્યુલેશનનું વર્ગીકરણ કરો',
    'Verified': 'ચકાસાયેલ',
    'High confidence': 'ઊંચો વિશ્વાસ',
    'Medium confidence': 'મધ્યમ વિશ્વાસ',
    'Low confidence': 'ઓછો વિશ્વાસ',
    'India': 'ભારત',
    'International': 'આંતરરાષ્ટ્રીય',
    'Both': 'બંને',
  },
  'pa': {
    'Hello! I am **AyurPedia**, your specialized AI assistant for Ayurvedic Intellectual Property Rights (IPR), Patent regulations, Traditional Knowledge Digital Library (TKDL) norms, and regulatory frameworks (e.g. FSSAI Ayurveda-Aahar, WIPO GRATK Treaty).\n\nYou can ask a regulatory or legal question directly, or use our **Classification Tool** to categorize your herbal formulation.': 'ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਮੈਂ **ਆਯੁਰਪੀਡੀਆ**, ਆਯੁਰਵੈਦ ਬੌਧਿਕ ਸੰਪੱਤੀ ਅਧਿਕਾਰ (IPR), ਪੇਟੈਂਟ ਨਿਯਮ, ਪਰੰਪਰਾਗਤ ਗਿਆਨ ਡਿਜੀਟਲ ਲਾਇਬ੍ਰੇਰੀ (TKDL) ਮਾਪਦੰਡ ਅਤੇ ਨਿਯਮਕ ਢਾਂਚੇ ਲਈ (ਜਿਵੇਂ FSSAI ਆਯੁਰਵੈਦ-ਆਹਾਰ, WIPO GRATK ਸੰਧੀ) ਤੁਹਾਡਾ ਵਿਸ਼ੇਸ਼ AI ਸਹਾਇਕ ਹਾਂ.\n\nਤੁਸੀਂ ਸਿੱਧੇ ਹੀ ਨਿਯਮਕ ਜਾਂ ਕਾਨੂਨੀ ਸਵਾਲ ਪੁੱਛ ਸਕਦੇ ਹੋ, ਜਾਂ ਤੁਹਾਡੇ ਜੜੀ-ਬੂਟੀ ਫਾਰਮੂਲੇਸ਼ਨ ਨੂੰ ਵਰਗੀਕਰਨ ਲਈ ਸਾਡੇ **ਵਰਗੀਕਰਨ ਟੂਲ** ਦੀ ਵਰਤੋਂ ਕਰ ਸਕਦੇ ਹੋ.',
    'Classify Formulation': 'ਫਾਰਮੂਲੇਸ਼ਨ ਵਰਗੀਕਰਨ',
    'Verified': 'ਪੁਸ਼ਟੀ ਕੀਤਾ',
    'High confidence': 'ਉੱਚ ਵਿਸ਼ਵਾਸ',
    'Medium confidence': 'ਮੱਧਮ ਵਿਸ਼ਵਾਸ',
    'Low confidence': 'ਘੱਟ ਵਿਸ਼ਵਾਸ',
    'India': 'ਭਾਰਤ',
    'International': 'ਅੰਤਰਰਾਸਟਰੀ',
    'Both': 'ਦੋਵੇਂ',
  },
  'or': {
    'Hello! I am **AyurPedia**, your specialized AI assistant for Ayurvedic Intellectual Property Rights (IPR), Patent regulations, Traditional Knowledge Digital Library (TKDL) norms, and regulatory frameworks (e.g. FSSAI Ayurveda-Aahar, WIPO GRATK Treaty).\n\nYou can ask a regulatory or legal question directly, or use our **Classification Tool** to categorize your herbal formulation.': 'ନମସ୍କାର! ମୁଁ **ଆୟୁର୍ପିଡିଆ**, ଆୟୁର୍ବେଦ ବୌଦ୍ଧିକ ସମ୍ପତ୍ତି ଅଧିକାର (IPR), ପେଟେଣ୍ଟ ନିୟମ, ପାରମ୍ପରିକ ଜ୍ଞାନ ଡିଜିଟାଲ ଲାଇବ୍ରେରୀ (TKDL) ମାନ୍ୟତା ଏବଂ ନିୟାମକ ଢାଞଚା ପାଇଁ (ଯେପରି FSSAI ଆୟୁର୍ବେଦ-ଆହାର, WIPO GRATK ସନ୍ଧି) ଆପଣଙ୍କ ବିଶେଷ AI ସହାୟକ।\n\nଆପଣ ସିଧାସଳଖ ନିୟାମକ କିମ୍ବା ଆଇନ ପ୍ରଶ୍ନ ପଚାରିପାରନ୍ତି, କିମ୍ବା ଆପଣଙ୍କ ଔଷଧୀୟ ଫର୍ମୁଲେସନ୍ ବର୍ଗୀକରଣ କରିବାକୁ ଆମର **ବର୍ଗୀକରଣ ସାଧନ** ବ୍ୟବହାର କରିପାରନ୍ତି।',
    'Classify Formulation': 'ଫର୍ମୁଲେସନ୍ ବର୍ଗୀକରଣ କରନ୍ତୁ',
    'Verified': 'ଯାଞ୍ଚ କରାଯାଇଛି',
    'High confidence': 'ଉଚ୍ଚ ବିଶ୍ୱାସ',
    'Medium confidence': 'ମଧ୍ୟମ ବିଶ୍ୱାସ',
    'Low confidence': 'କମ୍ ବିଶ୍ୱାସ',
    'India': 'ଭାରତ',
    'International': 'ଅନ୍ତର୍ଜାତୀୟ',
    'Both': 'ଉଭୟ',
  },
  'sa': {
    'Hello! I am **AyurPedia**, your specialized AI assistant for Ayurvedic Intellectual Property Rights (IPR), Patent regulations, Traditional Knowledge Digital Library (TKDL) norms, and regulatory frameworks (e.g. FSSAI Ayurveda-Aahar, WIPO GRATK Treaty).\n\nYou can ask a regulatory or legal question directly, or use our **Classification Tool** to categorize your herbal formulation.': 'नमस्कार! अहं **आयुर्पीडिया**, आयुर्वेद बौद्धिक सम्पदा अधिकाराणाम् (IPR), पेटेण्ट् नियमानाम्, परम्परागतज्ञानस्य डिजिटल् लाइब्रेरी (TKDL) मानकानाम् च नियामकरचनानाम् (यथा FSSAI आयुर्वेद-आहारः, WIPO GRATK सन्धिः) कृते भवतः विशिष्टः AI सहायकः।\n\nभवान् सरासरं नियामकं वा न्यायिकं प्रश्नं पृच्छितुं शक्नोति, अथवा भवतः औषधीयसंरचनायाः वर्गीकरणार्थं अस्माकं **वर्गीकरणसाधनस्य** उपयोगं कर्तुं शक्नोति।',
    'Classify Formulation': 'संरचनां वर्गीकुरु',
    'Verified': 'सत्यापितः',
    'High confidence': 'उच्चविश्वासः',
    'Medium confidence': 'मध्यमविश्वासः',
    'Low confidence': 'निम्नविश्वासः',
    'India': 'भारतः',
    'International': 'अन्तरराष्ट्रियः',
    'Both': 'उभयौ',
  },
};

/**
 * Translate text using Bhashini NMT API or smart offline translation.
 * 
 * @param {string} text - Text to translate
 * @param {string} sourceLang - Source language code (e.g. 'en', 'hi')
 * @param {string} targetLang - Target language code (e.g. 'hi', 'en')
 * @returns {Promise<string>} Translated text
 */
export const translateText = async (text, sourceLang = 'en', targetLang = 'hi') => {
  if (!text || sourceLang === targetLang) {
    return text;
  }

  const cacheKey = `${sourceLang}:${targetLang}:${text}`;
  if (translationCache.has(cacheKey)) {
    return translationCache.get(cacheKey);
  }

  // Check offline dictionary
  if (OFFLINE_DICTIONARY[targetLang] && OFFLINE_DICTIONARY[targetLang][text]) {
    const translation = OFFLINE_DICTIONARY[targetLang][text];
    translationCache.set(cacheKey, translation);
    return translation;
  }

  // If Bhashini API key is configured, call Bhashini
  if (BHASHINI_API_KEY && BHASHINI_API_KEY !== 'your_bhashini_api_key_here') {
    try {
      const response = await axios.post(
        `${BHASHINI_API_URL}/services/inference/pipeline`,
        {
          pipelineTasks: [
            {
              taskType: 'translation',
              config: {
                language: {
                  sourceLanguage: sourceLang,
                  targetLanguage: targetLang,
                },
                serviceId: BHASHINI_PIPELINE_ID || undefined,
              },
            },
          ],
          inputData: {
            input: [{ source: text }],
          },
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': BHASHINI_API_KEY,
            'userID': BHASHINI_USER_ID,
          },
          timeout: 10000,
        }
      );

      const translated = response.data?.pipelineResponse?.[0]?.output?.[0]?.target;
      if (translated) {
        translationCache.set(cacheKey, translated);
        return translated;
      }
    } catch (apiError) {
      console.warn('[Bhashini API] Translation failed, falling back to original/local text:', apiError.message);
    }
  }

  // Fallback: return original text (English/untranslated)
  translationCache.set(cacheKey, text);
  return text;
};

/**
 * Detect script / language of input text (heuristic)
 */
export const detectLanguage = (text) => {
  if (!text) return 'en';
  // Devanagari range: \u0900-\u097F
  if (/[\u0900-\u097F]/.test(text)) return 'hi';
  // Bengali: \u0980-\u09FF
  if (/[\u0980-\u09FF]/.test(text)) return 'bn';
  // Tamil: \u0B80-\u0BFF
  if (/[\u0B80-\u0BFF]/.test(text)) return 'ta';
  // Telugu: \u0C00-\u0C7F
  if (/[\u0C00-\u0C7F]/.test(text)) return 'te';
  // Kannada: \u0C80-\u0CFF
  if (/[\u0C80-\u0CFF]/.test(text)) return 'kn';
  // Malayalam: \u0D00-\u0D7F
  if (/[\u0D00-\u0D7F]/.test(text)) return 'ml';
  // Gujarati: \u0A80-\u0AFF
  if (/[\u0A80-\u0AFF]/.test(text)) return 'gu';
  // Gurmukhi (Punjabi): \u0A00-\u0A7F
  if (/[\u0A00-\u0A7F]/.test(text)) return 'pa';
  // Odia: \u0B00-\u0B7F
  if (/[\u0B00-\u0B7F]/.test(text)) return 'or';

  return 'en';
};

export default {
  SUPPORTED_LANGUAGES,
  translateText,
  detectLanguage,
};
