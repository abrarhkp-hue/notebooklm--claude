#!/usr/bin/env python3
"""Research automation example for notebooklm-py.

This script demonstrates the research automation workflow:
1. Create a notebook
2. Start deep research on a topic
3. Poll for results
4. Import selected sources into the notebook
5. Generate audio overview from imported sources

Prerequisites:
    pip install "notebooklm-py[browser]"
    playwright install chromium
    notebooklm login  # Authenticate first

Usage:
    python research_automation.py
"""

import asyncio

from notebooklm import NotebookLMClient


async def main():
    print("=== NotebookLM Research Automation ===\n")

    async with await NotebookLMClient.from_storage() as client:
        # 1. Create a notebook for research
        print("Creating research notebook...")
        nb = await client.notebooks.create("Deep Research: AI Ethics")
        print(f"  Created: {nb.id} - {nb.title}\n")

        # 2. Start deep research
        print("Starting deep research on 'AI ethics in healthcare'...")
        research_task = await client.research.start(
            nb.id, 
            query="AI ethics in healthcare",
            mode="deep"  # deep or fast
        )
        print(f"  Task ID: {research_task['task_id']}")
        print(f"  Report ID: {research_task.get('report_id', 'N/A')}")
        
        # 3. Poll for results
        print("\nPolling for research results...")
        while True:
            result = await client.research.poll(nb.id)
            
            if result["status"] == "no_research":
                print("  No research found, waiting...")
                await asyncio.sleep(10)
                continue
                
            print(f"  Status: {result['status']}")
            print(f"  Query: {result.get('query', 'N/A')}")
            print(f"  Sources found: {len(result.get('sources', []))}")
            
            if result["status"] == "completed":
                break
            elif result["status"] == "failed":
                print("  Research failed!")
                return
                
            await asyncio.sleep(15)  # Poll every 15 seconds
        
        # 4. Display research findings
        sources = result.get("sources", [])
        if sources:
            print("\n📚 Research Sources Found:")
            for i, src in enumerate(sources[:10], 1):  # Show first 10
                url = src.get("url", "No URL")
                title = src.get("title", "Untitled")
                print(f"  {i}. {title}")
                if url:
                    print(f"     {url}")
        
        # 5. Import selected sources
        # Filter to sources with URLs (required for import)
        importable_sources = [s for s in sources if s.get("url")]
        
        if importable_sources:
            print(f"\nImporting {len(importable_sources)} sources...")
            imported = await client.research.import_sources(
                nb.id,
                task_id=research_task["task_id"],
                sources=importable_sources[:5]  # Import first 5
            )
            print(f"  Imported: {len(imported)} sources")
            
            # 6. Generate audio overview
            print("\n🎙️ Generating audio overview...")
            artifact = await client.artifacts.generate_audio(
                nb.id,
                instructions="Create an engaging podcast about AI ethics in healthcare",
                format="deep-dive",
                length="long"
            )
            
            # Wait for completion
            print("  Waiting for generation (may take 2-5 minutes)...")
            final = await client.artifacts.wait_for_completion(
                nb.id, artifact.task_id, timeout=600, poll_interval=15
            )
            
            if final.is_complete:
                print(f"  ✅ Complete! Listen at: {final.url}")
            else:
                print(f"  Status: {final.status}")
        
        # Cleanup (optional)
        # print("\nCleaning up...")
        # await client.notebooks.delete(nb.id)
        
    print("\n=== Research Complete! ===")


if __name__ == "__main__":
    asyncio.run(main())
