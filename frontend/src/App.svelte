<script lang="ts">
  import { onMount } from 'svelte';
  import { tables } from './table';
  import { connectMqtt } from './mqtt';
  import { newId, short } from './lib/uuid';

  let client: any;

  function order(tableId: number) {
    const foodName = prompt('Food name?')?.trim();
    if (!foodName) return;

    const orderId = newId();

    // Optimistic: show in "Preparing"
    tables.update(t => {
      t[tableId].preparing = [...t[tableId].preparing, { name: foodName, id: orderId }];
      return t;
    });

    // Send ORDER event
    const msg = {
      v: 1,
      type: "ORDER",
      orderId,
      tableId,
      foodName,
      requestedAt: Date.now() / 1000
    };
    client.publish('orders/new', JSON.stringify(msg), { qos: 1 });
  }

  onMount(async () => {
    client = await connectMqtt();
    client.subscribe('food/ready', { qos: 1 });

    client.on('message', (topic: string, payload: Uint8Array) => {
      if (topic !== 'food/ready') return;
      const data = JSON.parse(new TextDecoder().decode(payload));
      const { tableId, orderId, foodName } = data;

      tables.update(t => {
        // remove from preparing by short id match
        t[tableId].preparing = t[tableId].preparing.filter(p => short(p.id) !== short(orderId));
        // add to ready
        t[tableId].ready = [...t[tableId].ready, foodName];
        return t;
      });
    });
  });
</script>

<h1>Brian's Restaurant</h1>

<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:16px">
  {#each [1,2,3,4] as id}
    <div style="border:1px solid #ddd;padding:12px;border-radius:8px">
      <h2>Table {id}</h2>
      <button on:click={() => order(id)}>ORDER</button>

      <h3>Preparing</h3>
      <ul>
        {#each $tables[id].preparing as p}
          <li>{p.name} ({p.id.slice(0,8)})</li>
        {/each}
        {#if $tables[id].preparing.length === 0}<li>—</li>{/if}
      </ul>

      <h3>Ready</h3>
      <ul>
        {#each $tables[id].ready as r}<li>{r}</li>{/each}
        {#if $tables[id].ready.length === 0}<li>—</li>{/if}
      </ul>
    </div>
  {/each}
</div>
