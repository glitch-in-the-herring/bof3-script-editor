# Writing for the Script Editor

## Alphanumeric
Use ASCII alphanumeric characters. No conversion takes place.

## Punctuations
Use ASCII punctuations. These are converted to the encoding format the game uses.

## Whitespace and Newline

## Textbox Position
Use
```
[POS <box_pos> <box_style>]
```
to indicate the style and position of a textbox.  
`<box_pos>` and `box_style` are two-character codes, The available options are:

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
