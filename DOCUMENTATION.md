# Script Editor Syntax

## Alphanumeric
Use ASCII alphanumeric characters. No conversion takes place.

## Punctuations
Use ASCII punctuations. These are converted to the encoding format the game uses.

## Whitespaces and Newlines
Use the ASCII whitespace (`0x20`). Use UNIX line endings.

## Pointer marker
To add an offset to the table pointer, use `==`. To mark the end of a string, use `\`.

## Commands
### Textbox Position
```
[POS <box_pos> <box_style>]
```
This command 

| Vertical `box_pos` | Position |
| ------------------ | -------- |
| `B_`               | Bottom   |
| `M_`               | Mid      | 
| `T_`               | Top      |

| Horizontal `box_pos` | Position |
| -------------------- | -------- |
| `_L`                 | Left     |
| `_M`                 | Mid      | 
| `_R`                 | Right    |

Example: `BM` means bottom (vertically)-mid (horizontally).

| `<box_style>` | Style                             |
| ------------- | --------------------------------- |
| `NV`          | Normal size, visible background   |
| `NI`          | Normal size, invisible background |
| `SV`          | Small size, visible background    |

### Text Color

### Placeholders