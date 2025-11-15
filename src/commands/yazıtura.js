const { SlashCommandBuilder, AttachmentBuilder } = require('discord.js');
const path = require('path');
const fs = require('fs');

module.exports = {
    data: new SlashCommandBuilder()
        .setName('yazıtura')
        .setDescription('Yazı-Tura atma simülasyonu.'),
    async execute(interaction) {
        const result = Math.random() < 0.5 ? 'heads' : 'tails';
        const imagePath = path.join(__dirname, '..', '..', 'yazıtura', `${result}.png`);

        if (fs.existsSync(imagePath)) {
            const attachment = new AttachmentBuilder(imagePath);
            await interaction.reply({ 
                content: result === 'heads' ? '🪙 **Yazı!**' : '🪙 **Tura!**',
                files: [attachment] 
            });
        } else {
            await interaction.reply(result === 'heads' ? '🪙 **Yazı!**' : '🪙 **Tura!**');
        }
    }
};
