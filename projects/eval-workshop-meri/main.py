import os
from datetime import datetime
from topics import TECHNICAL_TOPICS
from generator import generate_article


def main():
    # Create output directory if it doesn't exist
    output_dir = "generated_articles"
    os.makedirs(output_dir, exist_ok=True)

    # Get current timestamp for the batch
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print(f"Starting article generation batch at {timestamp}")
    print("-" * 50)

    for topic in TECHNICAL_TOPICS:
        try:
            print(f"\nGenerating article for: {topic['subject']}")
            article = generate_article(topic["subject"], topic["length"])

            # Create filename from topic
            filename = f"{topic['subject'].lower().replace(' ', '_')}_{timestamp}.html"
            filepath = os.path.join(output_dir, filename)

            # Save the article
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(article)

            print(f"✓ Successfully generated and saved to: {filename}")

        except Exception as e:
            print(f"✗ Error generating article for {topic['subject']}: {str(e)}")

    print("\nArticle generation complete!")
    print(f"Articles saved in: {output_dir}/")


if __name__ == "__main__":
    main()
