Gotcha — let’s redo the **How-to** file clean from top to bottom so it doesn’t break midway.

Here’s a fresh `HOWTO.md` you can paste directly:

````markdown
# How to Use the Master Reference Table

This guide explains how to use the **Master Reference Table** once it’s imported into a spreadsheet tool like **Google Sheets**, Excel, or Numbers.

The goal is to let you:

- Quickly generate **100-card Commander decks** for any of the 4 archetypes:
  - **GA4** (Azorius Prison),
  - **CA** (Bant Hatebears / Blink),
  - **SU** (Sultai Graveyard Value–Combo),
  - **RGX** (Simic Lands / Big Mana),
- Switch between **salt tiers** (Ext, Mid, Low),
- See overlaps and differences between decks,
- Customize lists for your own meta.

---

## 1. Table Structure & Columns

Your master table should have **at least** these columns (you may have extra ones like “Why” or “DollarCost”):

1. **Row**  
   Simple index number, mostly for reference.

2. **Name**  
   Exact card name (e.g., `Grand Arbiter Augustin IV`, `Winds of Abandon`).

3. **Type**  
   Card type line (e.g., `Creature — Human Wizard`, `Legendary Land`, `Enchantment — Aura`).

4. **Description**  
   Short summary of what the card does (not necessarily full Oracle text).

5. **Casting Cost**  
   Mana cost (e.g., `1U`, `3WW`, `XGG`, or `—` for lands).

6. **Decks**  
   **Comma-separated list** of deck tags that use this card.  
   Tags follow this pattern:

   - `GA4-Ext`, `GA4-Mid`, `GA4-Low`
   - `CA-Ext`, `CA-Mid`, `CA-Low`
   - `SU-Ext`, `SU-Mid`, `SU-Low`
   - `RGX-Ext`, `RGX-Mid`, `RGX-Low`

   Example:  
   `GA4-Ext,GA4-Mid,CA-Ext` means the card belongs to:
   - GA4 Extreme,
   - GA4 Mid,
   - CA Extreme.

7. **IsCommander**  
   `Y` if this card is a commander in at least one deck, `N` otherwise.

8. **DollarCost** (optional)  
   Approximate price. Used for total deck cost estimation.

9. **Why** (optional)  
   Short justification (“Prison piece vs creature decks”, “Primary finisher”, etc.).

---

## 2. Basic Setup in Google Sheets

Once you’ve imported the table into Google Sheets:

1. **Turn on Filter**
   - Select the header row.
   - Click **Data → Create a filter**.
   - Each header cell now has a filter icon.

2. **Freeze the Header**
   - Click **View → Freeze → 1 row**.
   - Keeps the header visible as you scroll.

3. **(Optional) Create a Filter View**
   - **Data → Filter views → Create new filter view**.
   - This lets you filter/sort without messing up anyone else’s view.

Now you can filter by archetype, salt tier, type, etc.

---

## 3. Building a 100-Card Deck for a Specific Archetype & Salt Tier

Example: you want to build **GA4-Ext** (Extreme-salt Azorius Prison).

### 3.1 Filter by Deck Tag

1. Click the filter icon on the **Decks** column.
2. Choose **Filter by condition → Text contains**.
3. Enter: `GA4-Ext`.
4. Apply.

Now the sheet shows only cards whose `Decks` cell includes `GA4-Ext`.

### 3.2 Identify the Commander

1. Click the filter icon on **IsCommander**.
2. Filter to **`Y`**.
3. You should see one (maybe more, if you allow multiple options) commander row — e.g., `Grand Arbiter Augustin IV`.

That’s your commander.

Then:

- Set **IsCommander** back to **Show all** (or `N` if you want to temporarily hide the commander row while counting non-commander cards).

### 3.3 Count Your Cards

Commander decks are:
- **1 commander** + **99 other cards**.

If your data range is `A2:H300` (adjust if needed), you can use a `SUBTOTAL` to count **only visible** rows (after filters):

```text
=SUBTOTAL(103, A2:A300)
````

* `103` = COUNTA for visible cells.
* This tells you how many rows are currently shown for that filter.

To get the count of **non-commander** cards:

* Either temporarily filter `IsCommander = N` and use the same `SUBTOTAL`,
* Or subtract 1 if you know there’s exactly one commander in view.

Target:

* 1 commander (`IsCommander = Y`)
* 99 non-commander cards in that filtered view.

If you see:

* **More than 99 non-commander cards** → you have a pool; you’ll cut down.
* **Fewer than 99 non-commander cards** → you need to add basics or extra cards (usually basics / flex slots).

---

## 4. Trimming & Customizing Decks

The master table is designed to give you a **slightly oversized pool** per deck/tier, so you can tune for your group.

### 4.1 What to Cut First

When you have **more than 99** non-commander rows:

1. **Flex / Meta slots**

   * Look for rows explicitly labeled as meta/flex (“Worldly small flex slots (meta)” or similar).
   * These are designed to be cut or swapped depending on your playgroup.

2. **Redundant Effects**

   * Scan the **Description** and **Type** columns:

     * Do you have 7 artifact removal spells? You might only want 4–5.
     * Too many board wipes? Keeping 3–5 is usually enough.

3. **High-Salt Cards for Casual Pods**

   * Use the README’s salt discussion:

     * Things like Tabernacle, Armageddon, hard-lock combos are great in Ext but miserable in Low.
   * Cut the saltiest cards when playing with precons or low-power groups.

4. **Curve Considerations**

   * Sort by **Casting Cost**:

     * Data → Sort range → sort by Casting Cost.
   * If the top-end is crowded (lots of 6+ drops), trim some for more early-game.

### 4.2 Using Type Filters

To sanity check your build composition:

* Filter `Type` → **Text contains `Land`**:

  * Count lands (35–38 is typical, adjusted for ramp density).
* Filter `Type` → **Text contains `Creature`**:

  * See creature count (depends on archetype; CA wants more creatures than GA4).
* Filter `Type` for other buckets: `Artifact`, `Enchantment`, `Instant`, `Sorcery`.

The **Type + Casting Cost** combination helps you spot if you’re overly heavy in, say, 5-mana enchantments or too light on 1–2-mana interaction.

---

## 5. Comparing Decks & Finding Overlaps

One of the big advantages of this master table is seeing **how decks overlap** and where they differ.

### 5.1 See All Cards for an Archetype (Regardless of Tier)

Example: all cards used by **any GA4 variant**:

1. Filter `Decks` → **Text contains** `GA4-`.
2. Now you see all cards that show up in **GA4-Ext**, **GA4-Mid**, or **GA4-Low**.

You can do this for any archetype:

* `CA-` for all CA cards.
* `SU-` for all SU cards.
* `RGX-` for all RGX cards.

### 5.2 Cards Shared by Two Specific Tiers

Example: cards in **both GA4-Ext and GA4-Mid**:

1. Add a helper column, say `InBoth`.

2. In row 2 of that column, enter (assuming `Decks` is column `F`):

   ```text
   =AND(
     ISNUMBER(SEARCH("GA4-Ext", F2)),
     ISNUMBER(SEARCH("GA4-Mid", F2))
   )
   ```

3. Fill this formula down.

4. Filter `InBoth` = `TRUE`.

Now you see cards **shared** by GA4-Ext and GA4-Mid. These are your **core GA4 cards**.

### 5.3 Cards Unique to a Tier

Example: cards **only** in GA4-Ext and not in Mid/Low:

1. Add helper column, e.g. `ExtOnly`.

2. Formula (again assuming `Decks` = column `F`):

   ```text
   =AND(
     ISNUMBER(SEARCH("GA4-Ext", F2)),
     NOT(ISNUMBER(SEARCH("GA4-Mid", F2))),
     NOT(ISNUMBER(SEARCH("GA4-Low", F2)))
   )
   ```

3. Fill down.

4. Filter `ExtOnly = TRUE`.

These rows are the **“spike cards”** that turn GA4-Mid into GA4-Ext:

* Most oppressive stax pieces,
* Fastest mana,
* Hardest locks.

You can repeat this pattern for:

* `CA-Ext` vs `CA-Mid/Low`,
* `SU-Ext` vs `SU-Mid/Low`,
* `RGX-Ext` vs `RGX-Mid/Low`.

---

## 6. Using Salt Tiers to Adjust Power for Your Meta

Because each card encodes **both archetype and salt tier** in the `Decks` column, you can treat salt tiers as a **swap list**.

### 6.1 Downgrading a Deck (e.g., Ext → Mid → Low)

Let’s say you own a **physical GA4 deck** that’s currently at **Ext**.

You want to play at a casual table and downgrade to **GA4-Low**.

1. **Show GA4-Low list**

   * Filter `Decks` → Text contains `GA4-Low`.
   * This is your **target deck**.

2. **Identify cards that are only in Ext**

   * Filter `Decks` → Text contains `GA4-Ext`.
   * Use the `ExtOnly` helper (Section 5.3) to see cards unique to Ext.

3. **Swap plan**

   * Cards with `ExtOnly = TRUE` are your candidates to **cut** when lowering power:

     * Hard stax,
     * RL bombs,
     * Combo finishers unsuited to casual pods.
   * Replace those with:

     * Cards from `GA4-Low` list that are not currently in your Ext build,
     * Or extra lands, cantrips, and fun/political cards.

You can do the same exercise for **CA**, **SU**, and **RGX**.

---

## 7. Estimating Deck Cost

If your table has a `DollarCost` column:

### 7.1 Total Cost for a Deck

1. Filter `Decks` → Text contains the desired tag (e.g., `CA-Mid`).
2. Confirm you’re looking at the full intended 100 cards (commander + 99).
3. Suppose `DollarCost` is in column `H`, rows `2:300`. Use:

   ```text
   =SUBTOTAL(109, H2:H300)
   ```

   * `109` is “SUM of visible cells only”.

This gives you the **total cost** for the currently filtered deck.

### 7.2 Comparing Costs Between Tiers

You can:

1. Filter `Decks` = `GA4-Ext`, sum DollarCost.
2. Filter `Decks` = `GA4-Mid`, sum DollarCost.
3. Filter `Decks` = `GA4-Low`, sum DollarCost.

Now you see:

* How much **price difference** there is between tiers.
* Which cards are driving cost (often RL lands, fast mana, and old staples).

---

## 8. Adding New Cards or Changing Deck Membership

As your meta evolves, you’ll want to:

* Add new cards,
* Move cards between salt tiers,
* Or assign cards to new decks.

### 8.1 Adding a New Card

1. Scroll to the bottom; choose the next empty row.

2. Fill:

   * **Row** – next index (e.g., 296 → 297).
   * **Name** – exact card name.
   * **Type** – type line.
   * **Description** – short functional summary.
   * **Casting Cost** – mana cost or `—` for lands.
   * **Decks** – comma-separated tags (e.g., `CA-Mid,CA-Low`).
   * **IsCommander** – `Y` or `N`.
   * **DollarCost / Why** – if you’re using those.

3. Check that `Decks` tags are spelled exactly like existing ones (e.g., `GA4-Mid`, *not* `GA4-mid`).

### 8.2 Moving a Card Between Tiers

Example: move a removal spell from **SU-Ext** to **SU-Mid**:

1. Find the row with that card.
2. Edit `Decks`:

   * Remove `SU-Ext`,
   * Add `SU-Mid`.
3. Now:

   * Filtering on `SU-Mid` will include it,
   * Filtering on `SU-Ext` will not (unless you leave it on both).

---

## 9. Exporting a Decklist for Use Elsewhere

Once a deck is filtered down and trimmed to 100 cards:

### 9.1 Copy/Paste Names

1. Filter for your deck (e.g., `RGX-Ext`).
2. Select the **Name** column cells for those rows.
3. Copy and paste into a text file.
4. Save as `RGX-Ext.txt` or similar.

This is often enough to import into sites like Moxfield, Archidekt, etc.

### 9.2 Download as CSV

1. Keep the filter (and optional filter view) active for your deck.
2. File → **Download → Comma-separated values (.csv)**.
3. Import that CSV into your deckbuilder of choice.

Some sites are picky about format, so you may want to strip extra columns or rename headers.

---

## 10. Quick Use-Case Recipes

### 10.1 “Show me CA-Mid and CA-Low overlap”

1. Add helper column `CA_Mid_Low`.

2. Formula (assuming `Decks` is column `F`):

   ```text
   =AND(
     ISNUMBER(SEARCH("CA-Mid", F2)),
     ISNUMBER(SEARCH("CA-Low", F2))
   )
   ```

3. Filter `CA_Mid_Low = TRUE`.

These are your **core CA cards** that appear in both Mid and Low.

---

### 10.2 “Show me anti-prison tech for countering GA4”

1. Filter `Decks` to look at **CA-Ext, CA-Mid, SU-Ext, RGX-Ext** (you can use text filters like `Text contains "CA-"` or multiple conditions if using filter views).
2. Sort or filter by **Description** for keywords:

   * `destroy target artifact`,
   * `destroy target enchantment`,
   * `each opponent`,
   * `cannot be countered`,
   * etc.
3. Use the **Why** column (if present) to spot cards labeled as:

   * “Anti-prison”
   * “Blows up stax piece”
   * “Versus GA4”

This gives you a quick **shopping list** for building GA4 predators.

---

### 10.3 “Build a casual SU-Low for a new group”

1. Filter `Decks` → Text contains `SU-Low`.
2. Check creature count (filter Type → contains `Creature`).
3. Check land count (filter Type → contains `Land`), add basics if needed.
4. Make sure most cards are **value-oriented** rather than hard combo:

   * Use the `Why` column to avoid harsh combos (e.g., Hulk piles, Breach loops).
5. Export the final list via copy/paste or CSV.

---

## 11. Mental Model: The Table as a Menu

Think of the Master Reference Table as:

* A **menu** of cards tagged by:

  * Archetype (GA4/CA/SU/RGX),
  * Salt tier (Ext/Mid/Low),
  * Role (via Description and Why),
* Rather than four static decklists.

Using filters and helper columns you can:

* Spin up **base decks** (e.g., GA4-Mid),
* Upgrade or downgrade via **tier-specific cards**,
* Adapt to new metas by:

  * Adding/removing tags in `Decks`,
  * Tweaking flex/meta slots,
  * Watching cost implications via `DollarCost`.

After a few uses, the workflow becomes:

> 1. Filter `Decks` to the archetype + tier.
> 2. Trim to 99 non-commander cards using flex/meta and salt-based cuts.
> 3. Export and sleeve.
> 4. If the table’s too strong or too weak, adjust using the same sheet.

That’s it — the Master Reference Table is your **living, filterable deck lab**.

```
```
