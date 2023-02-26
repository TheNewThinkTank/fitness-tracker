tableStyle = `
      <style>

      .exercise_name {
        display: grid;
        place-items: center;
      }

      table.GeneratedTable {
        width: 100%;
        background-color: #ffffff;
        border-collapse: collapse;
        border-width: 2px;
        border-color: #002fff;
        border-style: solid;
        color: #000000;
      }

      table.GeneratedTable :is(td, th) {
        border-width: 1px;
        border-color: #003cff;
        border-style: solid;
        padding: 3px;
      }

      table.GeneratedTable thead {
        background-color: #009dff;
      }

      </style>
`

class SetsTable extends HTMLElement {
  constructor() {
    super();
  }

  connectedCallback() {

    let tableHtml = `
    <h2 class="exercise_name">${this.getAttribute('exercise')}</h2>
    <table class="GeneratedTable">
      <thead>
        <tr>
          <th>set_number</th>
          <th>reps</th>
          <th>weight / kg</th>
        </tr>
      </thead>
      <tbody>
      `;

    let numberOfSets = parseInt(this.getAttribute('numberOfSets'))

    for (let i = 1; i <= numberOfSets; i++) {
      tableHtml += `<tr>
      <td class="exercise_name"><strong>${i}</strong></td>
      <td></td>
      <td></td>
    </tr>
    `
    }

    tableHtml += `
    </tbody>
    </table>
    `;

    this.innerHTML = tableStyle + tableHtml

  }
}

customElements.define('table-component', SetsTable);
