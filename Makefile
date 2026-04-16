.PHONY: sync-founding

# Copy canonical founding documents from the root project into anima-core.
# Run this whenever ANIMA.md, foundation/ethics.md, foundation/identity-initial.md,
# or foundation/origin.md change, before building or starting the container.
sync-founding:
	cp ANIMA.md anima-core/app/founding/anima.md
	cp foundation/ethics.md anima-core/app/founding/ethics.md
	cp foundation/identity-initial.md anima-core/app/founding/identity-initial.md
	cp foundation/origin.md anima-core/app/founding/origin.md
