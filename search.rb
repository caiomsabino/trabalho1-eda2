# search.rb
require 'json'

BLOCK_SIZE = 10

Product = Struct.new(:id, :name, :price)

input     = JSON.parse($stdin.read)
price_min = input["price_min"].to_f
price_max = input["price_max"].to_f

catalog = input["products"]
  .map { |p| Product.new(p["id"], p["name"], p["price"].to_f) }
  .sort_by(&:price)

index_1 = catalog.each_with_index
  .select { |_, i| i % BLOCK_SIZE == 0 }
  .map    { |_, i| i }

index_2 = index_1.each_with_index
  .select { |_, i| i % BLOCK_SIZE == 0 }
  .map    { |_, i| i }

def bin_lower(index_1, catalog, start, stop, target)
  lo, hi = start, stop
  while lo <= hi
    mid = (lo + hi) / 2
    catalog[index_1[mid]].price < target ? lo = mid + 1 : hi = mid - 1
  end
  lo
end

def bin_upper(index_1, catalog, start, stop, target)
  lo, hi = start, stop
  while lo <= hi
    mid = (lo + hi) / 2
    catalog[index_1[mid]].price <= target ? lo = mid + 1 : hi = mid - 1
  end
  lo - 1
end

def search_range(catalog, index_1, index_2, price_min, price_max)
  idx2_lo = 0; idx2_hi = index_2.size - 1

  # Binária no índice 2 — limite inferior
  lo, hi = 0, index_2.size - 1
  while lo <= hi
    mid = (lo + hi) / 2
    catalog[index_1[index_2[mid]]].price < price_min ? lo = mid + 1 : hi = mid - 1
  end
  idx2_lo = lo

  # Binária no índice 2 — limite superior
  lo, hi = 0, index_2.size - 1
  while lo <= hi
    mid = (lo + hi) / 2
    catalog[index_1[index_2[mid]]].price <= price_max ? lo = mid + 1 : hi = mid - 1
  end
  idx2_hi = lo - 1

  i1_start = [[idx2_lo - 1, 0].max * BLOCK_SIZE, 0].max
  i1_end   = [[idx2_hi + 1, index_2.size - 1].min * BLOCK_SIZE + BLOCK_SIZE - 1, index_1.size - 1].min

  i1_lo = bin_lower(index_1, catalog, i1_start, i1_end, price_min)
  i1_hi = bin_upper(index_1, catalog, i1_start, i1_end, price_max)

  seq_start = [[i1_lo - 1, 0].max * BLOCK_SIZE, 0].max
  seq_end   = [[i1_hi + 1, index_1.size - 1].min * BLOCK_SIZE + BLOCK_SIZE - 1, catalog.size - 1].min

  catalog[seq_start..seq_end].select { |p| p.price >= price_min && p.price <= price_max }
end

results = search_range(catalog, index_1, index_2, price_min, price_max)

if results.empty?
  puts "Nenhum produto encontrado."
else
  exact = price_min == price_max
  label = exact ? "Preço exato R$#{'%.2f' % price_min}" : "Range R$#{'%.2f' % price_min} – R$#{'%.2f' % price_max}"
  puts "#{label} → #{results.size} produto(s) encontrado(s):\n\n"
  results.each { |p| puts "  [#{p.id}] #{p.name} — R$#{'%.2f' % p.price}" }
end