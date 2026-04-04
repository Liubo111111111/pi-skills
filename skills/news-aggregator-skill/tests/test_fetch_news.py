import importlib.util
import pathlib
import unittest


MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "fetch_news.py"
SPEC = importlib.util.spec_from_file_location("fetch_news", MODULE_PATH)
fetch_news = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fetch_news)


SAMPLE_HF_HTML = """
<html>
  <body>
    <main>
      <div class="SVELTE_HYDRATER contents">
        <div class="ml-6 flex items-center overflow-hidden rounded-lg bg-gray-100 dark:bg-gray-800">
          <a href="/papers/date/2026-03-17" class="prev"></a>
          <div class="w-24 whitespace-nowrap text-center text-sm font-semibold text-gray-900 dark:text-gray-100">Mar 18</div>
        </div>
        <article class="relative flex flex-col overflow-hidden rounded-xl border">
          <a href="/papers/2603.16790" class="cover"></a>
          <div class="from-gray-50-to-white bg-linear-to-b -mt-2 flex px-6 pb-6 pt-8">
            <div class="w-full min-w-0">
              <h3>
                <a href="/papers/2603.16790">InCoder-32B: Code Foundation Model for Industrial Scenarios</a>
              </h3>
              <a href="/Beihang"><span>Beihang University</span></a>
              <a href="/papers/2603.16790">14</a>
              <a href="/papers/2603.16790#community">3</a>
            </div>
          </div>
        </article>
        <article class="relative flex flex-col overflow-hidden rounded-xl border">
          <a href="/papers/2603.13366" class="cover"></a>
          <div class="from-gray-50-to-white bg-linear-to-b -mt-2 flex px-6 pb-6 pt-8">
            <div class="w-full min-w-0">
              <h3>
                <a href="/papers/2603.13366">Thinking in Uncertainty: Mitigating Hallucinations in MLRMs</a>
              </h3>
              <a href="/OpenAI"><span>OpenAI</span></a>
              <a href="/papers/2603.13366">36</a>
              <a href="/papers/2603.13366#community">1</a>
            </div>
          </div>
        </article>
      </div>
    </main>
  </body>
</html>
"""


class ParseHuggingFaceItemsTests(unittest.TestCase):
    def test_extracts_items_and_metadata(self):
        items = fetch_news.parse_huggingface_items(SAMPLE_HF_HTML, limit=5)

        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["source"], "HuggingFace Papers")
        self.assertEqual(items[0]["title"], "InCoder-32B: Code Foundation Model for Industrial Scenarios")
        self.assertEqual(items[0]["url"], "https://huggingface.co/papers/2603.16790")
        self.assertEqual(items[0]["heat"], "14 likes | 3 comments | Beihang University")
        self.assertEqual(items[0]["time"], "2026-03-18")

    def test_keyword_filter_still_applies(self):
        items = fetch_news.parse_huggingface_items(SAMPLE_HF_HTML, limit=5, keyword="Hallucinations")

        self.assertEqual(len(items), 1)
        self.assertIn("Hallucinations", items[0]["title"])


if __name__ == "__main__":
    unittest.main()
